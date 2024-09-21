# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
# import re
import tempfile
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.support.ui import Select

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
            [1.0, 'foo', 5.0, 'left-palm', 33],
            [2.0, 'foo', 10.0, 'right-foot', 66],
            [3.0, 'bar', 15.0, 'gut', 55],
            [4.0, 'bar', 20.0, 'right-foot', 44],
            [5.0, 'baz', 25.0, 'left-palm', 77],
            [6.0, 'baz', 30.0, 'gut', 22]
        ]
        self.md = Metadata(pd.DataFrame(
            data=data, index=md_index, dtype=object,
            columns=['A', 'foobar', 'B', 'bodysite', 'Z']))

        # exp_marks_len = len(data)

        # TODO: re-work marks handling for rect marks
        self.test_cases = [
            ('bodysite', 'foobar', 'Z',
             # exp_marks_len, 150.0, 528.75,
             'bodysite', 'foobar', 'Z')
        ]

    # utility method that will run all checks for heatmap
    # used in each browser test below (firefox & chrome supported)
    def _selenium_heatmap_test(self, driver, x_measure, y_measure,
                               gradient_measure,
                               # exp_marks_len, exp_x_mark, exp_y_mark,
                               exp_x_measure, exp_y_measure,
                               exp_gradient_measure):
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
                                     'g[aria-roledescription="axis"]')
            self.assertEqual(len(axis_elements), 2)

            for _, axis in enumerate(axis_elements):
                label = axis.get_attribute('aria-label')
                if 'X-axis' in label:
                    self.assertIn(f"axis titled '{exp_x_measure}'", label)
                elif 'Y-axis' in label:
                    self.assertIn(f"axis titled '{exp_y_measure}'", label)
                else:
                    raise ValueError(f'Unexpected axis element {label} found.')

            # test that the legend contains the correct group
            legend_element = \
                driver.find_element(By.CSS_SELECTOR,
                                    'g[aria-roledescription="legend"]')

            label = legend_element.get_attribute('aria-label')
            self.assertIn(f"legend titled '{exp_gradient_measure}'", label)

            # TODO: re-work mark handling for heatmap rect marks
            # test that we have the correct number of marks
            # and that a mark is where we expect it to be
            # def _extract_transform_coordinates(transform_str):
            #     match = re.search(r'translate\(([^,]+),\s*([^)]+)\)',
            #                       transform_str)
            #     x = float(match.group(1))
            #     y = float(match.group(2))
            #     return x, y

            # mark_elements = \
            #     driver.find_elements(By.CSS_SELECTOR,
            #                          'g.marks > path[class^="mark-"]')
            # self.assertEqual(exp_marks_len, len(mark_elements))

            # mark_element_0 = \
            #     driver.find_element(By.CSS_SELECTOR,
            #                         'g.marks > path[class^="mark-0"]')
            # transform = mark_element_0.get_attribute('transform')

            # x_mark, y_mark = _extract_transform_coordinates(transform)

            # self.assertEqual(x_mark, exp_x_mark)
            # self.assertEqual(y_mark, exp_y_mark)

    # run selenium checks with a chrome driver
    def test_heatmap_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure, gradient_measure,
                 # exp_marks_len, exp_x_mark, exp_y_mark,
                 exp_x_measure, exp_y_measure,
                 exp_gradient_measure) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    gradient_measure=gradient_measure,
                    # exp_marks_len=exp_marks_len,
                    # exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_gradient_measure=exp_gradient_measure
                ):

                    self._selenium_heatmap_test(
                        driver, x_measure, y_measure, gradient_measure,
                        # exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_x_measure, exp_y_measure, exp_gradient_measure)

    # run selenium checks with a firefox driver
    def test_heatmap_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        with webdriver.Firefox(options=firefox_options) as driver:

            for (x_measure, y_measure, gradient_measure,
                 # exp_marks_len, exp_x_mark, exp_y_mark,
                 exp_x_measure, exp_y_measure,
                 exp_gradient_measure) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    gradient_measure=gradient_measure,
                    # exp_marks_len=exp_marks_len,
                    # exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_gradient_measure=exp_gradient_measure
                ):

                    self._selenium_heatmap_test(
                        driver, x_measure, y_measure, gradient_measure,
                        # exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_x_measure, exp_y_measure, exp_gradient_measure)
