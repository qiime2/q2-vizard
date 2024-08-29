# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, Metadata, Str, Choices, Bool
from q2_stats._type import Dist1D, Matched, Ordered

from q2_vizard.heatmap import plot_heatmap
from q2_vizard.scatterplot import scatterplot_2d
from q2_vizard.lineplot import lineplot


plugin = Plugin(name='vizard',
                version='0.0.1.dev0',
                website='https://github.com/qiime2/q2-vizard',
                package='q2_vizard',
                description='This QIIME 2 plugin is the first choice of wizard'
                            ' lizards for protection and entertainment.',
                short_description='The first choice of wizard lizards.')

# TODO: refactor
plugin.visualizers.register_function(
    function=plot_heatmap,
    inputs={'data': Dist1D[Ordered, Matched]},
    parameters={
        'transpose': Bool,
        'order': Str % Choices('ascending', 'descending')
    },
    name='Plot Heatmap',
    description='',
)


plugin.visualizers.register_function(
    function=scatterplot_2d,
    inputs={},
    parameters={
        'metadata': Metadata,
        'x_measure': Str,
        'y_measure': Str,
        'color_by': Str,
        'title': Str
    },
    name='2D Scatterplot',
    description='Basic 2D scatterplot for visualizing two numeric Metadata'
                ' measures with optional categorical color grouping.',
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least two'
                    ' numeric measures for visualizing.',
        'x_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the x-axis.',
        'y_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the y-axis.',
        'color_by': 'Categorical measure from the input Metadata that'
                    ' should be used for color-coding the scatterplot.',
        'title': 'The title of the scatterplot.'}
)


plugin.visualizers.register_function(
    function=lineplot,
    inputs={},
    parameters={
        'metadata': Metadata,
        'x_measure': Str,
        'y_measure': Str,
        'replicates': Bool,
        'average': Str % Choices('median', 'mean'),
        'facet_by': Str,
        'title': Str
    },
    name='Lineplot',
    description='Basic lineplot for visualizing two numeric Metadata'
                ' measures with optional faceting.',
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least two'
                    ' numeric measures for visualizing.',
        'x_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the x-axis.',
        'y_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the y-axis.',
        'replicates': 'Whether the chosen `x_measure` contains replicates.'
                      ' If true, a method for averaging the y(x) values must'
                      ' be selected.',
        'average': 'The method for averaging replicates'
                   ' if present in the chosen `x_measure`.'
                   ' Available methods are `median` and `mean`.',
        'facet_by': 'Categorical measure from the input Metadata that'
                    ' should be used for faceting the lineplot.',
        'title': 'The title of the lineplot.'}
)
