# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from .._util import _col_type_validation, _measure_validation


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()
        index = pd.Index(['sample1', 'sample2', 'sample3'],
                         name='sample-id')
        data = [
            [1.0, 'foo', 10],
            [2.0, 'bar', 20],
            [3.0, 'baz', 30]
        ]
        self.md = Metadata(pd.DataFrame(data=data, index=index, dtype=object,
                                        columns=['numeric-col',
                                                 'categorical-col',
                                                 'No.']))


class TestMeasureValidation(TestBase):
    def test_measure_not_in_metadata(self):
        with self.assertRaisesRegex(ValueError, '`boo` not found as a column'):
            _measure_validation(metadata=self.md, measure='boo')

    def test_measure_with_disallowed_char(self):
        with self.assertRaisesRegex(ValueError, '`No.` contains `.`'):
            _measure_validation(metadata=self.md, measure='No.')


class TestColTypeValidation(TestBase):
    def test_measure_not_categorical(self):
        with self.assertRaisesRegex(
            TypeError, '`categorical-col` not.*`NumericMetadataColumn`'
        ):
            _col_type_validation(metadata=self.md, measure='categorical-col',
                                 col_type='numeric')

    def test_measure_not_numeric(self):
        with self.assertRaisesRegex(
            TypeError, '`numeric-col` not.*`CategoricalMetadataColumn`'
        ):
            _col_type_validation(metadata=self.md, measure='numeric-col',
                                 col_type='categorical')
