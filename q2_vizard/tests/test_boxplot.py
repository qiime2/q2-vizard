# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import tempfile

from selenium import webdriver
# from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
# from selenium.webdriver.firefox.options import Options as FirefoxOptions

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

# from q2_vizard import boxplot


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('sample-md.tsv'))

        self.test_cases = [
            ('')
        ]

    def _selenium_boxplot_test(self, driver):
        with tempfile.TemporaryDirectory() as output_dir:
            # boxplot()

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

    def test_boxplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for () in self.test_cases:

                with self.subTest():

                    self._selenium_boxplot_test(driver)

    # def test_boxplot_firefox(self):
    #     firefox_options = FirefoxOptions()
    #     firefox_options.add_argument('-headless')

    #     self.assertGreater(len(self.test_cases), 0)

    #     with webdriver.Firefox(options=firefox_options) as driver:
    #         for () in self.test_cases:

    #             with self.subTest():

    #                 self._selenium_boxplot_test(driver)
