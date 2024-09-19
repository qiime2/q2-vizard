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
from q2_vizard.boxplot import boxplot


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
        'color_by_group': 'Categorical measure from the input Metadata that'
                          ' should be used for color-coding the scatterplot.',
        'title': 'The title of the scatterplot.'}
)


plugin.visualizers.register_function(
    function=boxplot,
    inputs={},
    parameters={
        'metadata': Metadata,
        'distribution': Str,
        'facet_by': Str,
        'average_method': Str % Choices('median', 'mean'),
        'whisker_range': Str % Choices('iqr', 'percentile'),
        'title': Str
    },
    name='Boxplot',
    description='Basic boxplot for visualizing a numeric Metadata measure'
                ' faceted by a categorical Metadata measure with choices for'
                ' average method and whisker range.',
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least one numeric measure'
                    ' and one categorical measure for visualizing.',
        'distribution': 'The numeric measure that will be used to create each'
                        ' box plot distribution.',
        'facet_by': 'The categorical measure that will be used to facet each'
                    ' group into separate box plots. If left blank, all data'
                    ' will be represented within a single box.',
        'average_method': 'The method that will be used to determine the'
                          ' average for each group represented. Options are'
                          ' either `mean` or `median` with `median` as the'
                          ' default.',
        'whisker_range': 'The range that will be used for calculating the'
                         ' whisker lengths for each box. Options are `iqr`'
                         ' or `percentile`. Any data points that fall outside'
                         ' of the chosen range will be represented as outliers'
                         ' plotted as circular points.',
        'title': 'The title of the boxplot.'
    }
)
