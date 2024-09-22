# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import tempfile

from qiime2.plugin.testing import TestPluginBase
from qiime2 import Metadata

from q2_vizard import lineplot


class TestLineplot(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.md = Metadata.load(self.get_data_path('lineplot-md.tsv'))

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
