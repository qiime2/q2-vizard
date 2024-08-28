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

from q2_vizard import lineplot


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()
        index = pd.Index(['sample1', 'sample2', 'sample3', 'sample4',
                          'sample5', 'sample6', 'sample7', 'sample8'],
                         name='sample-id')
        columns = ['numeric-col', 'categorical-col', 'replicate-groups',
                   'groups', 'replicates']
        data = [
            [1.0, 'foo', 1.0, 'group1', 1.0],
            [2.0, 'foo', 1.0, 'group1', 1.0],
            [3.0, 'bar', 2.0, 'group2', 1.0],
            [4.0, 'baz', 2.0, 'group2', 1.0],
            [5.0, 'foo', 3.0, 'group3', 1.0],
            [6.0, 'baz', 3.0, 'group3', 1.0],
            [7.0, 'baz', 4.0, 'group4', 1.0],
            [8.0, 'bar', 4.0, 'group4', 1.0]
        ]
        self.md = Metadata(pd.DataFrame(data=data, index=index,
                                        columns=columns, dtype=object))


class TestLineplot(TestBase):
    # TODO: refactor with replicate handling

    # def test_x_measure_no_group_with_replicates(self):
    #     with tempfile.TemporaryDirectory() as output_dir:
    #         with self.assertRaisesRegex(
    #                 ValueError, 'Replicates found in `replicates`.'):
    #             lineplot(output_dir=output_dir, metadata=self.md,
    #                      x_measure='replicates')

    # def test_x_measure_group_with_replicates(self):
    #     with tempfile.TemporaryDirectory() as output_dir:
    #         with self.assertRaisesRegex(
    #             ValueError, 'Replicates found in `replicates` within the'
    #             ' `group1` group.*chosen `group`: `groups`.'
    #         ):
    #             lineplot(output_dir=output_dir, metadata=self.md,
    #                      x_measure='replicates', group='groups')

    def test_y_measure_same_column_as_x_measure(self):
        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaisesRegex(
                ValueError, 'same column `numeric-col` has been used'
            ):
                lineplot(output_dir=output_dir, metadata=self.md,
                         x_measure='numeric-col', y_measure='numeric-col',
                         replicates=False)
