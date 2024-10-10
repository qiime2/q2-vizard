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
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
# from selenium.webdriver.firefox.options import Options as FirefoxOptions

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from q2_vizard import boxplot


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('sample-md.tsv'))

        # first/second cases are almost identical,
        # just w/different box_orientation & whisker_range params
        # third case doesn't include group, just producing a single box
        self.test_cases = [
            ('x', 'group', 'horizontal', "titled 'group'", None),
            ('x', 'group', 'vertical', "titled 'group'", 'minmax'),
            ('x', None, None, "titled 'legend'", 'tukeys_iqr')
        ]

    def _selenium_boxplot_test(
        self, driver, distribution_measure, group_by, box_orientation,
        exp_legend, whisker_range
        # exp_box_groups_len,
        # exp_whisker_lines_len, exp_whisker_caps_low_len,
        # exp_whisker_caps_high_len, exp_median_lines_len,
        # exp_total_outlier_marks_len, exp_single_box_outlier_marks_len,
        # exp_whisker_cap_low_mark, exp_whisker_cap_high_mark,
        # exp_median_mark, exp_outlier_mark_id,
        # exp_outlier_mark_group, exp_outlier_mark
    ):
        with tempfile.TemporaryDirectory() as output_dir:
            boxplot(
                output_dir=output_dir, metadata=self.md,
                distribution_measure=distribution_measure,
                group_by=group_by, box_orientation=box_orientation,
                whisker_range=whisker_range
            )

            # set defaults if None - for use in test validation
            if group_by is None:
                group_by = 'legend'
            if box_orientation is None:
                box_orientation = 'horizontal'
            if whisker_range is None:
                whisker_range = 'percentile'

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that our axes match xy input measures
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR, 'g.mark-group.role-axis')
            self.assertEqual(len(axis_elements), 2)

            for _, axis in enumerate(axis_elements):
                label = axis.get_attribute('aria-label')
                # assign xy measures based on box orientation
                if box_orientation == 'horizontal':
                    x_measure = distribution_measure
                    y_measure = group_by
                elif box_orientation == 'vertical':
                    x_measure = group_by
                    y_measure = distribution_measure
                # check for correct label on xy axes
                if 'X-axis' in label:
                    self.assertIn(f"axis titled '{x_measure}", label)
                elif 'Y-axis' in label:
                    self.assertIn(f"axis titled '{y_measure}'", label)

            # test that the legend contains the correct group
            legend_element = \
                driver.find_element(By.CSS_SELECTOR,
                                    'g.mark-group.role-legend')

            label = legend_element.get_attribute('aria-label')
            self.assertIn(exp_legend, label)

            # test that the subtitle contains the correct whisker_range method
            title_element = \
                driver.find_element(By.CSS_SELECTOR, 'g.mark-group.role-title')

            subtitle = title_element.get_attribute('subtitle')
            self.assertIn(whisker_range, subtitle)

            # TODO: still not working yet
            # test warning text is present when `suppressOutliers` is enabled
            # suppress_outliers = \
            #     driver.find_element(By.CSS_SELECTOR,
            #                         'input[name="suppressOutliers"]')

            # tspan_xpath = ("//tspan[contains(normalize-space(text()),"
            #                "'NOTE: Outliers have been suppressed.')]")

            # driver.execute_script("arguments[0].click();", suppress_outliers)

            # wait = WebDriverWait(driver, 10)
            # wait.until(EC.visibility_of_element_located((By.XPATH,
            #                                              tspan_xpath)))

            # tspan_element = driver.find_element(By.XPATH, tspan_xpath)

            # actual_text = tspan_element.text.strip()
            # exp_text = 'NOTE: Outliers have been suppressed.'

            # self.assertEqual(exp_text, actual_text)

    def test_boxplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (distribution_measure, group_by,
                 box_orientation, exp_legend,
                 whisker_range) in self.test_cases:

                with self.subTest(
                    distribution_measure=distribution_measure,
                    group_by=group_by, box_orientation=box_orientation,
                    exp_legend=exp_legend, whisker_range=whisker_range
                ):

                    self._selenium_boxplot_test(
                        driver, distribution_measure, group_by,
                        box_orientation, exp_legend, whisker_range)

    # def test_boxplot_firefox(self):
    #     firefox_options = FirefoxOptions()
    #     firefox_options.add_argument('-headless')

    #     self.assertGreater(len(self.test_cases), 0)

    #     with webdriver.Firefox(options=firefox_options) as driver:
    #         for () in self.test_cases:

    #             with self.subTest():

    #                 self._selenium_boxplot_test(driver)
