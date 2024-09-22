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

from q2_vizard import lineplot


class TestLineplot(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('lineplot-md.tsv'))
        exp_marks_len = self.md.id_count

        # first test case uses a replicates method & facet_by group
        # second test case doesn't have replicates or faceting
        self.test_cases = [
            ('x', 'y', 'facet', 'median', 'median', "titled 'facet'",
             ['aa', 'bb', 'cc'], exp_marks_len, '1', '2'),
            ('b', 'y', '', 'none', ' ', "titled 'legend'",
             '', exp_marks_len, '1', '6')
        ]

    # testing error handling within the actual method
    def test_y_measure_same_column_as_x_measure(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'same column `x` has been used'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='x')

    def test_x_replicates_with_faceting_error(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError,
                'Replicates found in `x` within the `aa` `facet_by` group'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='y', facet_by='facet')

    def test_x_replicates_without_faceting_error(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError,
                'Replicates found in `x`.'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='y')

    # selenium testing
    def _selenium_lineplot_test(self, driver, x_measure, y_measure,
                                facet_measure, replicate_method, exp_subtitle,
                                exp_legend, exp_facet_groups, exp_marks_len,
                                exp_x_mark, exp_y_mark):
        with tempfile.TemporaryDirectory() as output_dir:
            lineplot(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                facet_by=facet_measure,
                replicate_method=replicate_method
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that our axes match xy input measures
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g[aria-roledescription="axis"]')
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
                                    'g[aria-roledescription="legend"]')

            label = legend_element.get_attribute('aria-label')
            self.assertIn(exp_legend, label)

    # run selenium checks with a chrome driver
    def test_lineplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure, facet_measure, replicate_method,
                 exp_subtitle, exp_legend, exp_facet_groups, exp_marks_len,
                 exp_x_mark, exp_y_mark) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    facet_measure=facet_measure,
                    replicate_method=replicate_method,
                    exp_subtitle=exp_subtitle, exp_legend=exp_legend,
                    exp_facet_groups=exp_facet_groups,
                    exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark
                ):

                    self._selenium_lineplot_test(
                        driver, x_measure, y_measure, facet_measure,
                        replicate_method, exp_subtitle, exp_legend,
                        exp_facet_groups, exp_marks_len,
                        exp_x_mark, exp_y_mark)

    def test_lineplot_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        with webdriver.Firefox(options=firefox_options) as driver:
            for (x_measure, y_measure, facet_measure, replicate_method,
                 exp_subtitle, exp_legend, exp_facet_groups, exp_marks_len,
                 exp_x_mark, exp_y_mark) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    facet_measure=facet_measure,
                    replicate_method=replicate_method,
                    exp_subtitle=exp_subtitle, exp_legend=exp_legend,
                    exp_facet_groups=exp_facet_groups,
                    exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark
                ):

                    self._selenium_lineplot_test(
                        driver, x_measure, y_measure, facet_measure,
                        replicate_method, exp_subtitle, exp_legend,
                        exp_facet_groups, exp_marks_len,
                        exp_x_mark, exp_y_mark)
