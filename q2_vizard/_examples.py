# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import pkg_resources

import qiime2


def _get_data_from_tests(path):
    return pkg_resources.resource_filename('q2_vizard.tests',
                                           os.path.join('data', path))


def md_factory():
    return qiime2.Metadata.load(
        _get_data_from_tests('sample-md.tsv')
    )
