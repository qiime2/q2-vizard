# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
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
from selenium.webdriver.support.ui import Select

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from q2_vizard import lineplot


class TestLineplot(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('sample-md.tsv'))

        # sample01 is in group `aa`, the first of sorted [aa, bb, cc], so its
        # mark takes the first color of the palette in both cases
        # grouped: one line per group; ungrouped: a single `legend` group
        grouped = dict(group_by='group', exp_legend="titled 'group'")
        ungrouped = dict(group_by=None, exp_legend="titled 'legend'")

        # default palette is category10
        default_palette = dict(
            color_palette=None, exp_palette='category10',
            exp_fill='#1f77b4')
        # dark2 is used for the chosen palette because its first color
        # differs from category10's (category20 shares #1f77b4)
        chosen_palette = dict(
            color_palette='dark2', exp_palette='dark2',
            exp_fill='#1b9e77')

        median = dict(
            replicate_method='median',
            exp_subtitle='Data was averaged using the `median` method.')
        no_replicates = dict(replicate_method='none', exp_subtitle=' ')

        self.test_cases = {
            # replicate method & grouping, default palette
            'grouped_default_palette': dict(
                x_measure='x', y_measure='y',
                exp_x_mark='4', exp_y_mark='6', exp_y_measure='y',
                exp_line_strokes=['#1f77b4', '#ff7f0e', '#2ca02c'],
                **grouped, **median, **default_palette),
            # no y measure to test its default
            'grouped_default_y_measure': dict(
                x_measure='x', y_measure=None,
                exp_x_mark='4', exp_y_mark='4', exp_y_measure='x',
                exp_line_strokes=['#1f77b4', '#ff7f0e', '#2ca02c'],
                **grouped, **median, **default_palette),
            # no replicates & grouping, chosen palette
            # (`a` has no replicates within each group)
            'grouped_chosen_palette': dict(
                x_measure='a', y_measure='y',
                exp_x_mark='1', exp_y_mark='6', exp_y_measure='y',
                exp_line_strokes=['#1b9e77', '#d95f02', '#7570b3'],
                **grouped, **no_replicates, **chosen_palette),
            # no replicates or grouping, default palette
            'ungrouped_default_palette': dict(
                x_measure='b', y_measure='y',
                exp_x_mark='1', exp_y_mark='6', exp_y_measure='y',
                exp_line_strokes=['#1f77b4'],
                **ungrouped, **no_replicates, **default_palette),
            # no replicates or grouping, chosen palette
            'ungrouped_chosen_palette': dict(
                x_measure='b', y_measure='y',
                exp_x_mark='1', exp_y_mark='6', exp_y_measure='y',
                exp_line_strokes=['#1b9e77'],
                **ungrouped, **no_replicates, **chosen_palette),
        }

    # testing error handling within the actual method
    def test_y_measure_same_column_as_x_measure(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'same column `x` has been used'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='x')

    def test_x_replicates_with_grouping_error(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError,
                'Replicates found in `x` within the `aa` `group_by` group'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='y', group_by='group')

    def test_x_replicates_without_grouping_error(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError,
                'Replicates found in `x`.'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='x', y_measure='y')

    # selenium testing
    def _selenium_lineplot_test(self, driver, *, x_measure, y_measure,
                                group_by, replicate_method, color_palette,
                                exp_subtitle, exp_legend, exp_x_mark,
                                exp_y_mark, exp_y_measure, exp_palette,
                                exp_fill, exp_line_strokes):
        exp_marks_len = self.md.id_count
        exp_mark_id = 'sample01'

        # only pass a palette when one is chosen, so the default is used
        palette_kwargs = \
            {} if color_palette is None else {'color_palette': color_palette}

        with tempfile.TemporaryDirectory() as output_dir:
            lineplot(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                group_by=group_by,
                replicate_method=replicate_method,
                **palette_kwargs
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that we get the expected value in each dropdown
            def _dropdown_util(field, exp):
                dropdown = Select(driver.find_element(By.NAME, field))
                selected = dropdown.first_selected_option
                self.assertEqual(selected.get_attribute('value'), exp)

            _dropdown_util(field='yField', exp=exp_y_measure)
            _dropdown_util(field='colorPalette', exp=exp_palette)

            if y_measure is None:
                y_measure = exp_y_measure

            # test that our axes match xy input measures
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR, 'g.mark-group.role-axis')
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
            self.assertIn(exp_legend, label)

            # test that the title class contains the correct subtitle text
            title_element = \
                driver.find_element(By.CSS_SELECTOR, 'g.mark-group.role-title')

            subtitle = title_element.get_attribute('subtitle')
            self.assertEqual(subtitle, exp_subtitle)

            # test that the correct number of line marks are present
            # equal to the number of unique groups in the group_by, else = 1
            line_elements = \
                driver.find_elements(By.CSS_SELECTOR, 'g.mark-line.role-mark')
            md_df = self.md.to_dataframe()

            if group_by:
                exp_lines = len(md_df[group_by].unique())
            else:
                exp_lines = 1

            self.assertEqual(len(line_elements), exp_lines)

            # test that the lines are colored by the selected palette
            # (one color per group, in sorted group order)
            line_strokes = [
                line.get_attribute('stroke') for line in
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-line.role-mark > path')]
            self.assertEqual(sorted(line_strokes), sorted(exp_line_strokes))

            # test that the correct number of scatter marks are present
            # and a mark is where we expect it to be
            mark_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-symbol.role-mark > path')

            self.assertEqual(exp_marks_len, len(mark_elements))

            mark_element_0 = mark_elements[0]
            mark_id = mark_element_0.get_attribute('data-id')
            mark_x = mark_element_0.get_attribute('data-x')
            mark_y = mark_element_0.get_attribute('data-y')

            self.assertEqual(mark_id, exp_mark_id)
            self.assertEqual(mark_x, exp_x_mark)
            self.assertEqual(mark_y, exp_y_mark)

            # test that the selected palette reached the color scale
            self.assertEqual(mark_element_0.get_attribute('fill'), exp_fill)

            # check initial opacity for marks
            # opacity should be 1 unless `suppressMarks` checkbox is clicked
            for _, mark in enumerate(mark_elements):
                opacity = mark.get_attribute('opacity')
                self.assertEqual(opacity, '1')

            # mark opacity (post-checkbox clicked)
            # test warning text is present when `suppressMarks` is clicked
            checkbox = driver.find_element(By.CSS_SELECTOR,
                                           'input[name="suppressMarks"]')
            driver.execute_script("arguments[0].click();", checkbox)

            # Confirm the checkbox is selected
            self.assertTrue(checkbox.is_selected())

            page_source = driver.page_source
            exp_text = 'NOTE: Actual data marks have been suppressed.'

            self.assertIn(exp_text, page_source)

    def _run_browser_checks(self, driver):
        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        for name, case in self.test_cases.items():
            with self.subTest(case=name):
                self._selenium_lineplot_test(driver, **case)

    # run selenium checks with a chrome driver
    def test_lineplot_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        with webdriver.Chrome(options=chrome_options) as driver:
            self._run_browser_checks(driver)

    # run selenium checks with a firefox driver
    def test_lineplot_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        with webdriver.Firefox(options=firefox_options) as driver:
            self._run_browser_checks(driver)
