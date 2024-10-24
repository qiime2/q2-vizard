# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._version import get_versions

from q2_vizard.scatterplot import scatterplot_2d
from q2_vizard.heatmap import heatmap
from q2_vizard.lineplot import lineplot
from q2_vizard.boxplot import boxplot

__version__ = get_versions()['version']
del get_versions

__all__ = ['heatmap', 'scatterplot_2d', 'lineplot', 'boxplot']
