# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import tempfile
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import Select

from qiime2 import Metadata
from qiime2.plugin.testing import TestPluginBase

from q2_vizard.heatmap import heatmap


class TestHeatmap(TestPluginBase):
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

        shared = dict(
            x_measure='bodysite', y_measure='foobar', gradient_measure='Z',
            exp_x_mark='left-palm', exp_y_mark='foo', exp_gradient_mark='33')

        # continuous palettes render fills as rgb() strings
        self.test_cases = {
            # default palette (Viridis)
            'default_palette': dict(
                gradient_palette=None, exp_palette='Viridis',
                exp_fill='rgb(63, 73, 137)', **shared),
            'chosen_palette': dict(
                gradient_palette='Cividis', exp_palette='Cividis',
                exp_fill='rgb(47, 70, 110)', **shared),
            # `invertGradient` checkbox clicked after render: the scale is
            # reversed, so sample1's color comes from the opposite end
            'chosen_palette_inverted': dict(
                gradient_palette='Cividis', exp_palette='Cividis',
                invert_gradient=True,
                exp_fill='rgb(194, 179, 110)', **shared),
        }

    # utility method that will run all checks for heatmap
    # used in each browser test below (firefox & chrome supported)
    def _selenium_heatmap_test(self, driver, *, x_measure, y_measure,
                               gradient_measure, gradient_palette,
                               exp_x_mark, exp_y_mark, exp_gradient_mark,
                               exp_palette, exp_fill,
                               invert_gradient=False):
        exp_marks_len = self.md.id_count
        exp_mark_id = 'sample1'

        # only pass a palette when one is chosen, so the default is used
        palette_kwargs = ({} if gradient_palette is None
                          else {'gradient_palette': gradient_palette})

        with tempfile.TemporaryDirectory() as output_dir:
            heatmap(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                gradient_measure=gradient_measure,
                **palette_kwargs
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that the palette dropdown shows the expected palette
            palette_dropdown = \
                Select(driver.find_element(By.NAME, 'gradientPalette'))
            self.assertEqual(
                palette_dropdown.first_selected_option.get_attribute('value'),
                exp_palette)

            # test that our axes match the expected fields
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-group.role-axis')
            self.assertEqual(len(axis_elements), 2)

            for _, axis in enumerate(axis_elements):
                label = axis.get_attribute('aria-label')
                if 'X-axis' in label:
                    self.assertIn(f"axis titled '{x_measure}'", label)
                elif 'Y-axis' in label:
                    self.assertIn(f"axis titled '{y_measure}'", label)
                else:
                    raise ValueError(f'Unexpected axis element {label} found.')

            # test that the legend contains the correct group
            legend_element = \
                driver.find_element(By.CSS_SELECTOR,
                                    'g.mark-group.role-legend')

            label = legend_element.get_attribute('aria-label')
            self.assertIn(f"legend titled '{gradient_measure}'", label)

            # test that we have the correct number of rect marks
            # and that a rect mark is where we expect it to be
            mark_elements = \
                driver.find_elements(
                    By.CSS_SELECTOR, 'g.mark-rect.role-mark > path')
            self.assertEqual(exp_marks_len, len(mark_elements))

            mark_element_0 = mark_elements[0]
            mark_id = mark_element_0.get_attribute('data-id')
            mark_x = mark_element_0.get_attribute('data-x')
            mark_y = mark_element_0.get_attribute('data-y')
            mark_gradient = mark_element_0.get_attribute('data-gradient')

            self.assertEqual(mark_id, exp_mark_id)
            self.assertEqual(mark_x, exp_x_mark)
            self.assertEqual(mark_y, exp_y_mark)
            self.assertEqual(mark_gradient, exp_gradient_mark)

            # click the `invertGradient` checkbox when requested, which
            # reverses the color scale (unchecked by default)
            checkbox = driver.find_element(By.CSS_SELECTOR,
                                           'input[name="invertGradient"]')
            self.assertFalse(checkbox.is_selected())

            if invert_gradient:
                driver.execute_script("arguments[0].click();", checkbox)
                self.assertTrue(checkbox.is_selected())

            # test that the selected palette reached the color scale
            self.assertEqual(mark_element_0.get_attribute('fill'), exp_fill)

    def _run_browser_checks(self, driver):
        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        for name, case in self.test_cases.items():
            with self.subTest(case=name):
                self._selenium_heatmap_test(driver, **case)

    # run selenium checks with a chrome driver
    def test_heatmap_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        with webdriver.Chrome(options=chrome_options) as driver:
            self._run_browser_checks(driver)

    # run selenium checks with a firefox driver
    def test_heatmap_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        with webdriver.Firefox(options=firefox_options) as driver:
            self._run_browser_checks(driver)
