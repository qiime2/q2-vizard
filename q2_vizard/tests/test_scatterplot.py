# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase


class TestBase(TestPluginBase):
    package = 'q2_vizard.tests'


class TestScatterplot(TestBase):
    def test_input_measure_not_in_metadata():
        pass

    def test_input_measure_not_numeric_md_column():
        pass
