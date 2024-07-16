# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

import versioneer

setup(
    name='q2-vizard',
    version=versioneer.get_version(),
    packages=find_packages(),
    package_data={
        'q2_vizard': [
            'assets/*',
            'assets/heatmap/*',
            'assets/scatterplot_2d/*',
            'assets/curveplot/*'],
    },
    author='q2d2',
    author_email='q2d2@qiime2.org',
    description='QIIME 2 Plugin used for visualizations.',
    license='BSD-3-Clause',
    url='https://github.com/qiime2/q2-vizard',
    zip_safe=False,
    entry_points={
        'qiime2.plugins': ['q2-vizard=q2_vizard.plugin_setup:plugin']
    }
)
