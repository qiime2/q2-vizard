# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, Str, Metadata

from q2_vizard.heatmap import heatmap
from q2_vizard.scatterplot import scatterplot_2d

import q2_vizard._examples as ex

plugin = Plugin(name='vizard',
                version='0.0.1.dev0',
                website='https://github.com/qiime2/q2-vizard',
                package='q2_vizard',
                description='This QIIME 2 plugin is the first choice of wizard'
                            ' lizards for protection and entertainment.',
                short_description='The first choice of wizard lizards.')


plugin.visualizers.register_function(
    function=heatmap,
    inputs={},
    parameters={
        'metadata': Metadata,
        'x_measure': Str,
        'y_measure': Str,
        'gradient_measure': Str,
        'title': Str
    },
    name='Heatmap',
    description='Basic heatmap for visualizing three Metadata measures.',
    parameter_descriptions={
        'metadata': 'Any metadata-like input that contains at least three'
                    ' measures for visualizing, one of which must be numeric.',
        'x_measure': 'Numeric or categorical measure from the input Metadata'
                     ' that should be plotted on the x-axis.',
        'y_measure': 'Numeric or categorical measure from the input Metadata'
                     ' that should be plotted on the y-axis.',
        'gradient_measure': 'Numeric measure from the input Metadata that'
                            ' should be used to represent the color gradient'
                            ' in the heatmap.',
        'title': 'The title of the heatmap.'}
)


plugin.visualizers.register_function(
    function=scatterplot_2d,
    inputs={},
    parameters={
        'metadata': Metadata,
        'x_measure': Str,
        'y_measure': Str,
        'color_by_group': Str,
        'title': Str
    },
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least two'
                    ' numeric measures for visualizing.',
        'x_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the x-axis.',
        'y_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the y-axis.',
        'color_by_group': 'Categorical measure from the input Metadata that'
                          ' should be used for color-coding the scatterplot.',
        'title': 'The title of the scatterplot.'},
    name='2D Scatterplot',
    description='Basic 2D scatterplot for visualizing two numeric Metadata'
                ' measures with optional categorical color grouping.',
    examples={'scatterplot_defaults': ex.scatterplot_defaults,
              'scatterplot_all_measures': ex.scatterplot_all_measures}
)
