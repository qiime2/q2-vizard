# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, Metadata, Str

from q2_vizard._heatmap import plot_heatmap
from q2_vizard._scatterplot import plot_scatterplot

plugin = Plugin(name='vizard',
                version='0.0.1.dev0',
                website='https://github.com/qiime2/q2-vizard',
                description='This QIIME 2 plugin is the first choice of wizard'
                            ' lizards for protection and entertainment.',
                short_description='The first choice of wizard lizards.')


plugin.visualizers.register_function(
    function=plot_heatmap,
    inputs={
    },
    parameters={},
    name='Plot Heatmap',
    description='',
)


plugin.visualizers.register_function(
    function=plot_scatterplot,
    inputs={
    },
    parameters={
        'metadata': Metadata,
        'x_label': Str,
        'y_label': Str,
        'title': Str
    },
    name='Plot Scatterplot',
    description='',
)
