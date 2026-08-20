# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
import os
import tempfile
import re
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from qiime2 import Metadata
from qiime2.plugin.testing import TestPluginBase

from q2_vizard.scatterplot import scatterplot_2d
from .test_util import skip_selenium


class TestScatterplot(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        md_index = pd.Index(['sample1', 'sample2', 'sample3',
                             'sample4', 'sample5', 'sample6'],
                            name='sample-id')
        data = [
            [1, 'foo', 5, 'left-palm', 33],
            [2, 'foo', 10, 'right-foot', 66],
            [3, 'bar', 15, 'gut', 55],
            [4, 'bar', 20, 'right-foot', 44],
            [5, 'baz', 25, 'left-palm', 77],
            [6, 'baz', 30, 'gut', 22]
        ]
        self.md = Metadata(pd.DataFrame(
            data=data, index=md_index, dtype=object,
            columns=['A', 'foobar', 'B', 'bodysite', 'Z']))

        exp_marks_len = len(data)

        self.test_cases = [
            ('B', 'Z', 'foobar', exp_marks_len,
             '5', '33', 'sample1', 'B', 'Z', 'foobar', 'categorical'),
            ('B', 'Z', 'Z', exp_marks_len,
             '5', '33', 'sample1', 'B', 'Z', 'Z', 'continuous'),
            ('', '', '', exp_marks_len, '1', '1',
             'sample1', 'A', 'A', 'legendDefault', 'categorical')
        ]

    def test_missing_numeric_color_spec(self):
        edge_case_md = Metadata(pd.DataFrame(
            {
                'x': [1, 2, 3],
                'missing': [1.0, float('nan'), 3.0]
            },
            index=pd.Index(['sample1', 'sample2', 'sample3'],
                           name='sample-id')
        ))

        with tempfile.TemporaryDirectory() as output_dir:
            scatterplot_2d(output_dir=output_dir, metadata=edge_case_md,
                           color_by='missing')
            with open(os.path.join(output_dir, 'index.html')) as fh:
                page = fh.read()

        spec = json.loads(re.search(
            r'<script type="application/json" id="spec">\s*(.*?)\s*</script>',
            page, re.DOTALL
        ).group(1))
        fill = spec['marks'][0]['encode']['update']['fill']['signal']

        self.assertIn("'#808080'", fill)
        self.assertNotIn('isConstantNumericColorField', fill)

    # utility method that will run all checks for scatterplot
    # used in each browser test below (firefox & chrome supported)
    def _selenium_scatterplot_test(self, driver, x_measure, y_measure,
                                   color_measure, exp_marks_len, exp_x_mark,
                                   exp_y_mark, exp_mark_id, exp_x_measure,
                                   exp_y_measure, exp_color_measure,
                                   exp_color_mode):
        with tempfile.TemporaryDirectory() as output_dir:
            scatterplot_2d(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                color_by=color_measure
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that we get the expected value in each dropdown
            def _dropdown_util(field, exp):
                dropdown = Select(driver.find_element(By.NAME, field))
                selected = dropdown.first_selected_option.text
                self.assertEqual(selected, exp)

            dropdown_fields = [
                ('xField', exp_x_measure),
                ('yField', exp_y_measure),
                ('colorBy', exp_color_measure)
            ]

            for field_name, expected_value in dropdown_fields:
                _dropdown_util(field=field_name, exp=expected_value)

            # test that our axes match the dropdown values
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-group.role-axis')
            self.assertEqual(len(axis_elements), 2)

            for _, axis in enumerate(axis_elements):
                label = axis.get_attribute('aria-label')
                if 'X-axis' in label:
                    self.assertIn(f"axis titled '{exp_x_measure}'", label)
                elif 'Y-axis' in label:
                    self.assertIn(f"axis titled '{exp_y_measure}'", label)
                else:
                    raise ValueError(f'Unexpected axis element {label} found.')

            # Only the matching native legend is present in the SVG.
            legend_elements = driver.find_elements(
                By.CSS_SELECTOR, 'g.mark-group.role-legend'
            )
            self.assertEqual(len(legend_elements), 1)
            legend_element = legend_elements[0]
            label = legend_element.get_attribute('aria-label')
            self.assertIn(f"legend titled '{exp_color_measure}'", label)

            # The one palette control exposes schemes appropriate to the
            # selected color-field type.
            palette_options = [
                option.text for option in Select(
                    driver.find_element(By.NAME, 'colorPalette')
                ).options
            ]
            if exp_color_mode == 'continuous':
                self.assertEqual(
                    palette_options,
                    ['Viridis', 'Cividis', 'Magma', 'Plasma', 'Inferno']
                )
            else:
                self.assertNotIn('Viridis', palette_options)
                self.assertIn('category10', palette_options)

            # Switching color-field types updates the options in the same
            # palette control; it does not create a second palette dropdown.
            color_by_select = Select(driver.find_element(By.NAME, 'colorBy'))
            color_by_select.select_by_visible_text('Z')
            WebDriverWait(driver, 10).until(
                lambda _: Select(
                    driver.find_element(By.NAME, 'colorPalette')
                ).options[0].text == 'Viridis'
            )
            palette_options = [
                option.text for option in Select(
                    driver.find_element(By.NAME, 'colorPalette')
                ).options
            ]
            self.assertEqual(
                palette_options,
                ['Viridis', 'Cividis', 'Magma', 'Plasma', 'Inferno']
            )

            color_by_select = Select(driver.find_element(By.NAME, 'colorBy'))
            color_by_select.select_by_visible_text('foobar')
            WebDriverWait(driver, 10).until(
                lambda _: Select(
                    driver.find_element(By.NAME, 'colorPalette')
                ).options[0].text == 'category10'
            )
            palette_options = [
                option.text for option in Select(
                    driver.find_element(By.NAME, 'colorPalette')
                ).options
            ]
            self.assertNotIn('Viridis', palette_options)
            self.assertIn('category10', palette_options)

            # test that we have the correct number of marks
            # and that a mark is where we expect it to be
            mark_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-symbol.role-mark.marks > path')
            self.assertEqual(exp_marks_len, len(mark_elements))

            mark_element_0 = mark_elements[0]
            mark_id = mark_element_0.get_attribute('data-id')
            mark_x = mark_element_0.get_attribute('data-x')
            mark_y = mark_element_0.get_attribute('data-y')

            self.assertEqual(mark_id, exp_mark_id)
            self.assertEqual(mark_x, exp_x_mark)
            self.assertEqual(mark_y, exp_y_mark)

    # run selenium checks with a chrome driver
    @skip_selenium
    def test_scatterplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure, exp_color_measure,
                 exp_color_mode) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure,
                    exp_color_mode=exp_color_mode
                ):

                    self._selenium_scatterplot_test(
                        driver, x_measure, y_measure, color_measure,
                        exp_marks_len, exp_x_mark, exp_y_mark, exp_mark_id,
                        exp_x_measure, exp_y_measure, exp_color_measure,
                        exp_color_mode)

    # run selenium checks with a firefox driver
    @skip_selenium
    def test_scatterplot_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Firefox(options=firefox_options) as driver:

            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure, exp_color_measure,
                 exp_color_mode) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure,
                    exp_color_mode=exp_color_mode
                ):

                    self._selenium_scatterplot_test(
                        driver, x_measure, y_measure, color_measure,
                        exp_marks_len, exp_x_mark, exp_y_mark, exp_mark_id,
                        exp_x_measure, exp_y_measure, exp_color_measure,
                        exp_color_mode)
