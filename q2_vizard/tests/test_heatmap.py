# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
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

        exp_marks_len = len(data)

        self.test_cases = [
            ('bodysite', 'foobar', 'Z',
             exp_marks_len, 'left-palm', 'foo', '33',
             'data-sample1')
        ]

    # utility method that will run all checks for heatmap
    # used in each browser test below (firefox & chrome supported)
    def _selenium_heatmap_test(self, driver, x_measure, y_measure,
                               gradient_measure, exp_marks_len, exp_x_mark,
                               exp_y_mark, exp_gradient_mark, exp_mark_class):
        with tempfile.TemporaryDirectory() as output_dir:
            heatmap(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                gradient_measure=gradient_measure
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

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
            mark_class = mark_element_0.get_attribute('class')
            mark_x = mark_element_0.get_attribute('data-x')
            mark_y = mark_element_0.get_attribute('data-y')
            mark_gradient = mark_element_0.get_attribute('data-gradient')

            self.assertEqual(mark_class, exp_mark_class)
            self.assertEqual(mark_x, exp_x_mark)
            self.assertEqual(mark_y, exp_y_mark)
            self.assertEqual(mark_gradient, exp_gradient_mark)

    # run selenium checks with a chrome driver
    def test_heatmap_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure,
                 gradient_measure, exp_marks_len, exp_x_mark,
                 exp_y_mark, exp_gradient_mark,
                 exp_mark_class) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    gradient_measure=gradient_measure,
                    exp_marks_len=exp_marks_len, exp_x_mark=exp_x_mark,
                    exp_y_mark=exp_y_mark, exp_gradient_mark=exp_gradient_mark,
                    exp_mark_class=exp_mark_class
                ):

                    self._selenium_heatmap_test(
                        driver, x_measure, y_measure,
                        gradient_measure, exp_marks_len, exp_x_mark,
                        exp_y_mark, exp_gradient_mark, exp_mark_class)

    # run selenium checks with a firefox driver
    def test_heatmap_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Firefox(options=firefox_options) as driver:
            for (x_measure, y_measure,
                 gradient_measure, exp_marks_len, exp_x_mark,
                 exp_y_mark, exp_gradient_mark,
                 exp_mark_class) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    gradient_measure=gradient_measure,
                    exp_marks_len=exp_marks_len, exp_x_mark=exp_x_mark,
                    exp_y_mark=exp_y_mark, exp_gradient_mark=exp_gradient_mark,
                    exp_mark_class=exp_mark_class
                ):

                    self._selenium_heatmap_test(
                        driver, x_measure, y_measure,
                        gradient_measure, exp_marks_len, exp_x_mark,
                        exp_y_mark, exp_gradient_mark, exp_mark_class)
