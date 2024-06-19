# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import tempfile

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from q2_vizard import scatterplot_2d


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()
        index = pd.Index(['sample1', 'sample2', 'sample3'],
                         name='sample-id')
        data = [
            [1.0, 'foo'],
            [2.0, 'bar'],
            [3.0, 'baz']
        ]
        self.md = Metadata(pd.DataFrame(data=data, index=index, dtype=object,
                                        columns=['numeric-col',
                                                 'categorical-col']))


class TestScatterplot2D(TestBase):
    def test_x_measure_not_in_metadata(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(ValueError,
                                        '"boo" not found as a column'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, x_measure='boo')

    def test_y_measure_not_in_metadata(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(ValueError,
                                        '"boo" not found as a column'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, y_measure='boo')

    def test_color_by_group_not_in_metadata(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(ValueError,
                                        '"boo" not found as a column'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, color_by_group='boo')

    def test_x_measure_not_numeric_md_column(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(TypeError,
                                        '"categorical-col" not of type'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, x_measure='categorical-col')

    def test_y_measure_not_numeric_md_column(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(TypeError,
                                        '"categorical-col" not of type'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, y_measure='categorical-col')

    def test_group_measure_not_categorical_md_column(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(TypeError,
                                        '"numeric-col" not of type'):
                scatterplot_2d(output_dir=output_dir,
                               metadata=self.md, color_by_group='numeric-col')
