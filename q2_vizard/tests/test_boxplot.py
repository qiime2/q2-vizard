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
            ('x', 'group', 'horizontal', "titled 'group'", None, 3),
            ('x', 'group', 'vertical', "titled 'group'", 'minmax', 0),
            ('x', None, None, "titled 'legend'", 'tukeys_iqr', 0)
        ]

    def _selenium_boxplot_test(
        self, driver, distribution_measure, group_by, box_orientation,
        exp_legend, whisker_range, exp_total_outlier_marks_len
        # exp_single_box_outlier_marks_len,
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

            # MARKS - expected counts for each type
            md = self.md.to_dataframe()

            # boxGroup length
            boxGroup_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="boxGroup"]')

            if group_by == 'legend':
                exp_groups_len = 1
            else:
                exp_groups_len = len(md[group_by].unique())

            self.assertEqual(len(boxGroup_elements), exp_groups_len)

            # whiskerLine length - equal to unique vals in group_by column
            whiskerLine_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="whiskerLine"]')

            self.assertEqual(len(whiskerLine_elements), exp_groups_len)

            # whiskerCap lengths - equal to each other & exp_groups_len
            whiskerCapLow_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="whiskerCapLow"]')
            whiskerCapHigh_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="whiskerCapHigh"]')

            self.assertEqual(
                len(whiskerCapLow_elements), len(whiskerCapHigh_elements)
            )
            self.assertEqual(len(whiskerCapHigh_elements), exp_groups_len)

            # medianLine length - equal to unique vals in group_by column
            medianLine_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="medianLine"]')
            self.assertEqual(len(medianLine_elements), exp_groups_len)

            # outlierMark len
            outlierMark_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'path[aria-label="outlierMark"]')

            self.assertEqual(
                len(outlierMark_elements), exp_total_outlier_marks_len
            )

            # FOR A SINGLE BOX, checks for accuracy on all mark values
            boxGroup_element_0 = boxGroup_elements[0]
            whiskerLine_element_0 = whiskerLine_elements[0]
            whiskerCapLow_element_0 = whiskerCapLow_elements[0]
            whiskerCapHigh_element_0 = whiskerCapHigh_elements[0]
            medianLine_element_0 = medianLine_elements[0]

            # Group checks for a single box
            box0_group = boxGroup_element_0.get_attribute('data-group')

            # whiskerLine
            whiskerLine0_group = \
                whiskerLine_element_0.get_attribute('data-group')
            self.assertEqual(whiskerLine0_group, box0_group)

            # whiskerCap
            whiskerLow0_group = \
                whiskerCapLow_element_0.get_attribute('data-group')
            self.assertEqual(whiskerLow0_group, box0_group)

            whiskerHigh0_group = \
                whiskerCapHigh_element_0.get_attribute('data-group')
            self.assertEqual(whiskerHigh0_group, box0_group)

            # medianLine
            medianLine0_group = \
                medianLine_element_0.get_attribute('data-group')
            self.assertEqual(medianLine0_group, box0_group)

            # outlierMark - just confirming expected number in group0

            # TODO: stats checks
            # box0_q1 = boxGroup_element_0.get_attribute('data-q1')
            # box0_q3 = boxGroup_element_0.get_attribute('data-q3')

            # OUTLIER MARKS - these go last for checkbox handling
            # test warning text is present when `suppressOutliers` is clicked
            checkbox = driver.find_element(By.CSS_SELECTOR,
                                           'input[name="suppressOutliers"]')
            driver.execute_script("arguments[0].click();", checkbox)

            # Confirm the checkbox is selected
            self.assertTrue(checkbox.is_selected())

            page_source = driver.page_source
            exp_text = 'NOTE: Outliers have been suppressed.'

            self.assertIn(exp_text, page_source)

            # test that outlier marks are transparent while checkbox is clicked
            if len(outlierMark_elements) > 0:
                for _, mark in enumerate(outlierMark_elements):
                    opacity = mark.get_attribute('opacity')
                    self.assertEqual(opacity, '0')

    def test_boxplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (distribution_measure, group_by,
                 box_orientation, exp_legend, whisker_range,
                 exp_total_outlier_marks_len) in self.test_cases:

                with self.subTest(
                    distribution_measure=distribution_measure,
                    group_by=group_by, box_orientation=box_orientation,
                    exp_legend=exp_legend, whisker_range=whisker_range,
                    exp_total_outlier_marks_len=exp_total_outlier_marks_len
                ):

                    self._selenium_boxplot_test(
                        driver, distribution_measure, group_by,
                        box_orientation, exp_legend, whisker_range,
                        exp_total_outlier_marks_len)

    # def test_boxplot_firefox(self):
    #     firefox_options = FirefoxOptions()
    #     firefox_options.add_argument('-headless')

    #     self.assertGreater(len(self.test_cases), 0)

    #     with webdriver.Firefox(options=firefox_options) as driver:
    #         for () in self.test_cases:

    #             with self.subTest():

    #                 self._selenium_boxplot_test(driver)
