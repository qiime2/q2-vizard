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

from q2_vizard.scatterplot import scatterplot_2d, scatterplot_correlation


class TestScatterplot(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        md_index = pd.Index(['sample1', 'sample2', 'sample3',
                             'sample4', 'sample5', 'sample6'],
                            name='sample-id')
        data = [
            [1, 'foo', 5, 'left-palm', 33, 0.1, 0.01],
            [2, 'foo', 10, 'right-foot', 66, 0.3, 0.03],
            [3, 'bar', 15, 'gut', 55, -0.2, 0.02],
            [4, 'bar', 20, 'right-foot', 44, -0.7, 0.033],
            [5, 'baz', 25, 'left-palm', 77, 0, 0.025],
            [6, 'baz', 30, 'gut', 22, 0.7, -0.05]
        ]
        self.md = Metadata(pd.DataFrame(
            data=data, index=md_index, dtype=object,
            columns=['A', 'foobar', 'B', 'bodysite', 'Z', 'C', 'F']))

        exp_marks_len = len(data)

        self.test_cases = [
            ('B', 'Z', 'foobar', exp_marks_len,
             '5', '33', 'sample1', 'B', 'Z', 'foobar'),
            ('B', 'Z', 'A', exp_marks_len,
             '5', '33', 'sample1', 'B', 'Z', 'A'),
            ('', '', '', exp_marks_len, '1', '1',
             'sample1', 'A', 'A', 'legendDefault')
        ]

    # utility method that will run all checks for each scatterplot method
    # used in browser tests under each child class (firefox & chrome supported)
    def _selenium_scatterplot_test(self, driver, plot_method, x_measure,
                                   y_measure, color_measure, exp_marks_len,
                                   exp_x_mark, exp_y_mark, exp_mark_id,
                                   exp_x_measure, exp_y_measure,
                                   exp_color_measure):
        with tempfile.TemporaryDirectory() as output_dir:
            plot_method(
                output_dir=output_dir, metadata=self.md,
                x_measure=x_measure, y_measure=y_measure,
                color_by=color_measure
            )

            driver.get(f"file://{os.path.join(output_dir, 'index.html')}")

            # test that we get the expected value in each dropdown
            def _dropdown_util(field, exp):
                dropdown = Select(driver.find_element(By.NAME, field))
                selected = dropdown.first_selected_option.text
                self.assertEqual(selected, exp)

            dropdown_fields = [
                ('xField', exp_x_measure),
                ('yField', exp_y_measure),
                ('colorBy', exp_color_measure)
            ]

            for field_name, expected_value in dropdown_fields:
                _dropdown_util(field=field_name, exp=expected_value)

            # test that our axes match the dropdown values
            axis_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-group.role-axis')
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
            # both the categorical & the numeric legend are always rendered,
            # but only the one matching the colorBy column is titled
            legend_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-group.role-legend')
            self.assertEqual(len(legend_elements), 2)

            labels = [legend.get_attribute('aria-label')
                      for legend in legend_elements]
            titled = [label for label in labels
                      if f"legend titled '{exp_color_measure}'" in label]
            self.assertEqual(len(titled), 1)

            # test that we have the correct number of marks
            # and that a mark is where we expect it to be
            mark_elements = \
                driver.find_elements(By.CSS_SELECTOR,
                                     'g.mark-symbol.role-mark.marks > path')
            self.assertEqual(exp_marks_len, len(mark_elements))

            mark_element_0 = mark_elements[0]
            mark_id = mark_element_0.get_attribute('data-id')
            mark_x = mark_element_0.get_attribute('data-x')
            mark_y = mark_element_0.get_attribute('data-y')

            self.assertEqual(mark_id, exp_mark_id)
            self.assertEqual(mark_x, exp_x_mark)
            self.assertEqual(mark_y, exp_y_mark)


class TestScatterplot2D(TestScatterplot):
    package = 'q2_vizard.tests'

    def setUp(self):
        return super().setUp()

    # run selenium checks with a chrome driver
    def test_scatterplot_2d_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure, exp_color_measure) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure
                ):

                    self._selenium_scatterplot_test(
                        driver, scatterplot_2d, x_measure, y_measure,
                        color_measure, exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_mark_id, exp_x_measure, exp_y_measure,
                        exp_color_measure)

    # run selenium checks with a firefox driver
    def test_scatterplot_2d_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.test_cases), 0)

        with webdriver.Firefox(options=firefox_options) as driver:

            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure, exp_color_measure) in self.test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure
                ):

                    self._selenium_scatterplot_test(
                        driver, scatterplot_2d, x_measure, y_measure,
                        color_measure, exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_mark_id, exp_x_measure, exp_y_measure,
                        exp_color_measure)


class TestScatterplotCorrelation(TestScatterplot):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        exp_marks_len = self.md.id_count

        # C & F are the only columns in range [-1, 1]
        # so they're the only valid xy measures here
        # third test case doesn't include xy measures to test their defaults,
        # which both fall back to the first in-range column C
        self.correlation_test_cases = [
            ('C', 'F', 'foobar', exp_marks_len,
             '0.1', '0.01', 'sample1', 'C', 'F', 'foobar'),
            ('C', 'F', 'A', exp_marks_len,
             '0.1', '0.01', 'sample1', 'C', 'F', 'A'),
            ('', '', '', exp_marks_len, '0.1', '0.1',
             'sample1', 'C', 'C', 'legendDefault')
        ]

    # validate error handling within the actual method
    def test_x_measure_not_within_bounds(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'B values not bounded within range'
            ):
                scatterplot_correlation(output_dir=output_dir,
                                        metadata=self.md,
                                        x_measure='B', y_measure='C')

    def test_y_measure_not_within_bounds(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'Z values not bounded within range'
            ):
                scatterplot_correlation(output_dir=output_dir,
                                        metadata=self.md,
                                        x_measure='C', y_measure='Z')

    def test_no_numeric_measures_within_bounds(self):
        md_index = pd.Index(['sample1', 'sample2', 'sample3'],
                            name='sample-id')
        data = [
            [1, 'foo', 5],
            [2, 'foo', 10],
            [3, 'bar', 15]
        ]
        md = Metadata(pd.DataFrame(
            data=data, index=md_index, dtype=object,
            columns=['A', 'foobar', 'B']))

        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'None of the numeric columns in your metadata'
            ):
                scatterplot_correlation(output_dir=output_dir, metadata=md)

    # utility method for the checks that are unique to the correlation plot,
    # run after the shared checks in `_selenium_scatterplot_test`
    def _selenium_correlation_test(self, driver, exp_marks_len):
        # test that both correlation circles are drawn, and that the
        # `correlationCircles` signal controls their opacity
        circle_selectors = [
            'g.mark-arc.role-mark.correlation_circle_radius_0_5 > path',
            'g.mark-arc.role-mark.correlation_circle_radius_1 > path'
        ]

        circle_elements = [driver.find_element(By.CSS_SELECTOR, selector)
                           for selector in circle_selectors]
        self.assertEqual(len(circle_elements), 2)

        def _circle_opacity_util(exp):
            for circle in circle_elements:
                self.assertEqual(circle.get_attribute('opacity'), exp)

        toggle = driver.find_element(By.NAME, 'correlationCircles')

        # the signal is checked by default, so the circles start visible
        self.assertTrue(toggle.is_selected())
        _circle_opacity_util(exp='1')

        # signal unchecked updates the opacity to zero
        toggle.click()
        self.assertFalse(toggle.is_selected())
        _circle_opacity_util(exp='0')

        # test that every plotted mark falls within range [-1, 1] on both axes
        mark_elements = \
            driver.find_elements(By.CSS_SELECTOR,
                                 'g.mark-symbol.role-mark.marks > path')
        self.assertEqual(exp_marks_len, len(mark_elements))

        for mark in mark_elements:
            mark_id = mark.get_attribute('data-id')
            mark_x = float(mark.get_attribute('data-x'))
            mark_y = float(mark.get_attribute('data-y'))

            for axis, value in [('x', mark_x), ('y', mark_y)]:
                self.assertGreaterEqual(
                    value, -1,
                    f'{axis} value {value} for mark {mark_id} is below -1.')
                self.assertLessEqual(
                    value, 1,
                    f'{axis} value {value} for mark {mark_id} is above 1.')

        # test that the dashed center lines are drawn at x=0 & y=0
        # the xy domains are symmetrical around 0, so the center lines are
        # at 0 when each one crosses the midpoint of the other
        x_line = \
            driver.find_element(By.CSS_SELECTOR,
                                'g.mark-rule.role-mark.x_line_center > line')
        y_line = \
            driver.find_element(By.CSS_SELECTOR,
                                'g.mark-rule.role-mark.y_line_center > line')

        x_line_rect = x_line.rect
        y_line_rect = y_line.rect

        # each center line is straight - the horizontal one has no height,
        # and the vertical one has no width
        self.assertAlmostEqual(x_line_rect['height'], 0, delta=1)
        self.assertAlmostEqual(y_line_rect['width'], 0, delta=1)

        # the vertical line sits at the horizontal midpoint of the
        # horizontal line, and vice versa
        self.assertAlmostEqual(
            y_line_rect['x'],
            x_line_rect['x'] + x_line_rect['width'] / 2, delta=1)
        self.assertAlmostEqual(
            x_line_rect['y'],
            y_line_rect['y'] + y_line_rect['height'] / 2, delta=1)

    # run selenium checks with a chrome driver
    def test_scatterplot_correlation_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.correlation_test_cases), 0)

        with webdriver.Chrome(options=chrome_options) as driver:
            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure,
                 exp_color_measure) in self.correlation_test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure
                ):

                    self._selenium_scatterplot_test(
                        driver, scatterplot_correlation, x_measure, y_measure,
                        color_measure, exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_mark_id, exp_x_measure, exp_y_measure,
                        exp_color_measure)

                    self._selenium_correlation_test(driver, exp_marks_len)

    # run selenium checks with a firefox driver
    def test_scatterplot_correlation_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.add_argument('-headless')

        # saves someone a headache in the future if this is ever empty
        self.assertGreater(len(self.correlation_test_cases), 0)

        with webdriver.Firefox(options=firefox_options) as driver:

            for (x_measure, y_measure, color_measure, exp_marks_len,
                 exp_x_mark, exp_y_mark, exp_mark_id, exp_x_measure,
                 exp_y_measure,
                 exp_color_measure) in self.correlation_test_cases:

                with self.subTest(
                    x_measure=x_measure, y_measure=y_measure,
                    color_measure=color_measure, exp_marks_len=exp_marks_len,
                    exp_x_mark=exp_x_mark, exp_y_mark=exp_y_mark,
                    exp_mark_id=exp_mark_id, exp_x_measure=exp_x_measure,
                    exp_y_measure=exp_y_measure,
                    exp_color_measure=exp_color_measure
                ):

                    self._selenium_scatterplot_test(
                        driver, scatterplot_correlation, x_measure, y_measure,
                        color_measure, exp_marks_len, exp_x_mark, exp_y_mark,
                        exp_mark_id, exp_x_measure, exp_y_measure,
                        exp_color_measure)

                    self._selenium_correlation_test(driver, exp_marks_len)
