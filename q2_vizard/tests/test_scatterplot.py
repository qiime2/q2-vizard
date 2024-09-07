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
from selenium.webdriver.support.ui import Select

from qiime2 import Metadata
from qiime2.plugin.testing import TestPluginBase

from q2_vizard.scatterplot import scatterplot_2d


class TestScatterplot(TestPluginBase):
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

        self.test_cases = [
            ('B', 'Z', 'foobar', 'B', 'Z', 'foobar'),
            ('', '', '', 'A', 'A', 'legendDefault')
        ]

    # utility method that will run all checks for scatterplot
    # used in each browser test below (firefox & chrome supported)
    def _selenium_scatterplot_test(self, driver, x, y, color,
                                   exp_x, exp_y, exp_color):
        with tempfile.TemporaryDirectory() as output_dir:
            scatterplot_2d(
                output_dir=output_dir, metadata=self.md,
                x_measure=x, y_measure=y, color_by_group=color
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that we get the expected value in each dropdown
            def _dropdown_util(field, exp):
                dropdown = Select(driver.find_element(By.NAME, field))
                selected = dropdown.first_selected_option.text
                self.assertEqual(selected, exp)

            dropdown_fields = [
                ('xField', exp_x),
                ('yField', exp_y),
                ('colorBy', exp_color)
            ]

            for field_name, expected_value in dropdown_fields:
                _dropdown_util(field=field_name, exp=expected_value)

    def _print_mark_positions(self, driver):
        marks = driver.find_elements(By.CSS_SELECTOR, "circle")

        # Print the positions of each mark (cx and cy for <circle>)
        for mark in marks:
            actual_x = mark.get_attribute("cx")
            actual_y = mark.get_attribute("cy")
            raise ValueError(f"Mark position: x = {actual_x}, y = {actual_y}")

    # run selenium checks with a chrome driver
    def test_scatterplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        with webdriver.Chrome(options=chrome_options) as driver:
            self._print_mark_positions(driver)

            for x, y, color, exp_x, exp_y, exp_color in self.test_cases:
                with self.subTest(x=x, y=y, color=color, exp_x=exp_x,
                                  exp_y=exp_y, exp_color=exp_color):
                    self._selenium_scatterplot_test(driver, x, y, color,
                                                    exp_x, exp_y, exp_color)

    # run selenium checks with a firefox driver
    def test_scatterplot_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        with webdriver.Firefox(options=firefox_options) as driver:
            for x, y, color, exp_x, exp_y, exp_color in self.test_cases:
                with self.subTest(x=x, y=y, color=color, exp_x=exp_x,
                                  exp_y=exp_y, exp_color=exp_color):
                    self._selenium_scatterplot_test(driver, x, y, color,
                                                    exp_x, exp_y, exp_color)