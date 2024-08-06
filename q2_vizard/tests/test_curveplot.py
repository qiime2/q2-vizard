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

from q2_vizard import curveplot


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()


class TestCurveplot(TestBase):
    def test_x_measure_not_in_metadata(self):
        pass

    def test_x_measure_not_numeric_md_column(self):
        pass

    def test_x_measure_no_group_with_replicates(self):
        pass

    def test_x_measure_group_with_replicates(self):
        pass

    def test_y_measure_not_in_metadata(self):
        pass

    def test_y_measure_not_numeric_md_column(self):
        pass

    def test_group_measure_not_categorical_md_column(self):
        pass
