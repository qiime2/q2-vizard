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
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from q2_vizard import boxplot
from .._util import (_calculate_median, _calculate_quartiles,
                     _calculate_percentile)


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('sample-md.tsv'))

        # first/second cases are almost identical,
        # just w/different box_orientation & whisker_range params
        # third case doesn't include group, just producing a single box
        self.test_cases = [
            ('x', 'group', 'horizontal', "titled 'group'", None, 3, 1),
            ('x', 'group', 'vertical', "titled 'group'", 'minmax', 0, 0),
            ('x', None, None, "titled 'legend'", 'tukeys_iqr', 0, 0)
        ]

    def _selenium_boxplot_test(
        self, driver, distribution_measure, group_by, box_orientation,
        exp_legend, whisker_range, exp_total_outlier_marks_len,
        exp_single_box_outlier_marks_len
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
            # check initial opacity for outliers
            # opacity should be 1 unless `suppressOutliers` checkbox is clicked
            for _, mark in enumerate(outlierMark_elements):
                opacity = mark.get_attribute('opacity')
                self.assertEqual(opacity, '1')

            # outlier marks (post-checkbox clicked)
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

            # outlierMark - confirming expected number in group0
            outlier0_marks = []
            for _, mark in enumerate(outlierMark_elements):
                if mark.get_attribute('data-group') == box0_group:
                    outlier0_marks.append(mark)
            self.assertEqual(len(outlier0_marks),
                             exp_single_box_outlier_marks_len)

            # STATS CHECKS
            # Manual stats checks for dist_measure on each unique group_by
            if group_by != 'legend':
                # Group the data by the specified 'group_by' column
                grouped_data = md.groupby(group_by)
                results = {}

                for group_name, group_df in grouped_data:
                    # Sort the distribution_measure values for current group
                    sorted_values = (group_df[distribution_measure]
                                     .sort_values().reset_index(drop=True))

                    # Perform calculations
                    median = _calculate_median(sorted_values)
                    q1, q3 = _calculate_quartiles(sorted_values)
                    iqr = q3 - q1
                    percentile_9 = _calculate_percentile(sorted_values, 9)
                    percentile_91 = _calculate_percentile(sorted_values, 91)

                    # Determine lower and upper whiskers based on whisker_range
                    if whisker_range == 'tukeys_iqr':
                        lower_whisker = \
                            max((q1 - 1.5 * iqr), sorted_values.iloc[0])
                        upper_whisker = \
                            min((q3 + 1.5 * iqr), sorted_values.iloc[-1])
                    elif whisker_range == 'percentile':
                        lower_whisker = percentile_9
                        upper_whisker = percentile_91
                    elif whisker_range == 'minmax':
                        lower_whisker = sorted_values.iloc[0]
                        upper_whisker = sorted_values.iloc[-1]

                    # Identify outliers based on the chosen whisker_range
                    outliers = (sorted_values[(sorted_values < lower_whisker) |
                                (sorted_values > upper_whisker)].tolist())

                    # Store the results for the current group
                    results[group_name] = {
                        'minimum': sorted_values.iloc[0],
                        'maximum': sorted_values.iloc[-1],
                        'median': median,
                        'q1': q1,
                        'q3': q3,
                        'iqr': iqr,
                        'lower_whisker': lower_whisker,
                        'upper_whisker': upper_whisker,
                        'outliers': outliers,
                        'percentile_9': percentile_9,
                        'percentile_91': percentile_91
                    }
            else:
                # No grouping specified; run stats on the entire dataset
                sorted_values = (md[distribution_measure].sort_values()
                                 .reset_index(drop=True))

                # Perform calculations on the whole dataset
                median = _calculate_median(sorted_values)
                q1, q3 = _calculate_quartiles(sorted_values)
                iqr = q3 - q1
                percentile_9 = _calculate_percentile(sorted_values, 9)
                percentile_91 = _calculate_percentile(sorted_values, 91)

                # Determine lower and upper whiskers based on whisker_range
                if whisker_range == 'tukeys_iqr':
                    lower_whisker = \
                        max((q1 - 1.5 * iqr), sorted_values.iloc[0])
                    upper_whisker = \
                        min((q3 + 1.5 * iqr), sorted_values.iloc[-1])
                elif whisker_range == 'percentile':
                    lower_whisker = percentile_9
                    upper_whisker = percentile_91
                elif whisker_range == 'minmax':
                    lower_whisker = sorted_values.iloc[0]
                    upper_whisker = sorted_values.iloc[-1]

                # Identify outliers based on the chosen whisker_range
                outliers = (sorted_values[(sorted_values < lower_whisker) |
                            (sorted_values > upper_whisker)].tolist())

                # Store the results with a default group name or key
                results = {
                    'minimum': sorted_values.iloc[0],
                    'maximum': sorted_values.iloc[-1],
                    'median': median,
                    'q1': q1,
                    'q3': q3,
                    'iqr': iqr,
                    'lower_whisker': lower_whisker,
                    'upper_whisker': upper_whisker,
                    'outliers': outliers,
                    'percentile_9': percentile_9,
                    'percentile_91': percentile_91
                }

            # data handling for single vs. multi-group results
            if group_by != 'legend':
                res = results[box0_group]
            else:
                res = results

            # assertions for q1/q3
            box0_q1 = boxGroup_element_0.get_attribute('data-q1')
            box0_q3 = boxGroup_element_0.get_attribute('data-q3')

            self.assertEqual(res['q1'], float(box0_q1))
            self.assertEqual(res['q3'], float(box0_q3))

            # assertions for lower whisker/cap
            whisker0_low = \
                whiskerLine_element_0.get_attribute('data-low')
            whiskerCap0_low = \
                whiskerCapLow_element_0.get_attribute('data-val')

            self.assertEqual(whisker0_low, whiskerCap0_low)
            self.assertEqual(res['lower_whisker'], float(whisker0_low))

            # assertions for higher whisker/cap
            whisker0_high = \
                whiskerLine_element_0.get_attribute('data-high')
            whiskerCap0_high = \
                whiskerCapHigh_element_0.get_attribute('data-val')

            self.assertEqual(whisker0_high, whiskerCap0_high)
            self.assertEqual(res['upper_whisker'], float(whisker0_high))

            # assertion for median
            median0 = \
                medianLine_element_0.get_attribute('data-median')

            self.assertEqual(res['median'], float(median0))

            # assertions for outliers
            exp_outliers = sorted(res['outliers'])

            # Filter outlier marks that belong to group0
            outlier0_marks = \
                [mark for mark in outlierMark_elements
                 if mark.get_attribute('data-group') == box0_group]

            actual_outliers = []

            for mark in outlier0_marks:
                value = mark.get_attribute('data-val')
                if value is not None:
                    actual_outliers.append(float(value))

            actual_outliers = sorted(actual_outliers)

            self.assertEqual(len(exp_outliers), len(actual_outliers))

            for exp, obs in zip(exp_outliers, actual_outliers):
                self.assertEqual(exp, obs)

    # run selenium tests using a headless chrome driver
    def test_boxplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (distribution_measure, group_by,
                 box_orientation, exp_legend, whisker_range,
                 exp_total_outlier_marks_len,
                 exp_single_box_outlier_marks_len) in self.test_cases:

                with self.subTest(
                    distribution_measure=distribution_measure,
                    group_by=group_by, box_orientation=box_orientation,
                    exp_legend=exp_legend, whisker_range=whisker_range,
                    exp_total_outlier_marks_len=exp_total_outlier_marks_len,
                    exp_single_box_outlier_marks_len=(
                        exp_single_box_outlier_marks_len)
                ):

                    self._selenium_boxplot_test(
                        driver, distribution_measure, group_by,
                        box_orientation, exp_legend, whisker_range,
                        exp_total_outlier_marks_len,
                        exp_single_box_outlier_marks_len)

    # run selenium tests using a headless firefox driver
    def test_boxplot_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Firefox(options=firefox_options) as driver:
            for (distribution_measure, group_by,
                 box_orientation, exp_legend, whisker_range,
                 exp_total_outlier_marks_len,
                 exp_single_box_outlier_marks_len) in self.test_cases:

                with self.subTest(
                    distribution_measure=distribution_measure,
                    group_by=group_by, box_orientation=box_orientation,
                    exp_legend=exp_legend, whisker_range=whisker_range,
                    exp_total_outlier_marks_len=exp_total_outlier_marks_len,
                    exp_single_box_outlier_marks_len=(
                        exp_single_box_outlier_marks_len)
                ):

                    self._selenium_boxplot_test(
                        driver, distribution_measure, group_by,
                        box_orientation, exp_legend, whisker_range,
                        exp_total_outlier_marks_len,
                        exp_single_box_outlier_marks_len)
