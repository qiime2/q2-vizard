# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Plugin, Str, Metadata, Choices

from q2_vizard.heatmap import heatmap
from q2_vizard.scatterplot import scatterplot_2d
from q2_vizard.lineplot import lineplot
from q2_vizard.boxplot import boxplot

import q2_vizard._examples as ex

plugin = Plugin(name='vizard',
                version='0.0.1.dev0',
                website='https://github.com/qiime2/q2-vizard',
                package='q2_vizard',
                description='This QIIME 2 plugin is the first choice of wizard'
                            ' lizards for generalized microbiome data'
                            ' visualization!',
                short_description='Generalized microbiome data visualization.')


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
        'title': 'The title of the heatmap.'},
    name='Heatmap',
    description='Basic heatmap for visualizing three Metadata measures.',
    examples={'heatmap': ex.heatmap}
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
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least two'
                    ' numeric measures for visualizing.',
        'x_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the x-axis.',
        'y_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the y-axis.',
        'color_by': 'Categorical measure from the input Metadata that'
                    ' should be used for color-coding the scatterplot.',
        'title': 'The title of the scatterplot.'},
    name='2D Scatterplot',
    description='Basic 2D scatterplot for visualizing two numeric Metadata'
                ' measures with optional categorical color grouping.',
    examples={'scatterplot_defaults': ex.scatterplot_defaults,
              'scatterplot_all_measures': ex.scatterplot_all_measures}
)


plugin.visualizers.register_function(
    function=lineplot,
    inputs={},
    parameters={
        'metadata': Metadata,
        'x_measure': Str,
        'y_measure': Str,
        'replicate_method': Str % Choices('none', 'median', 'mean'),
        'group_by': Str,
        'title': Str
    },
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least two'
                    ' numeric measures for visualizing.',
        'x_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the x-axis.',
        'y_measure': 'Numeric measure from the input Metadata that should be'
                     ' plotted on the y-axis.',
        'replicate_method': 'The method for averaging replicates'
                            ' if present in the chosen `x_measure`.'
                            ' Available methods are `median` and `mean`.',
        'group_by': 'Categorical measure from the input Metadata that'
                    ' should be used for grouping the lineplot.',
        'title': 'The title of the lineplot.'},
    name='Lineplot',
    description='Basic lineplot for visualizing two numeric Metadata'
                ' measures with optional grouping. All numeric columns present'
                ' in the Metadata will be available as drop-down options on'
                ' the Y-axis, but the chosen `x_measure` remains fixed.',
    examples={
        f.__name__: f for f in [
            ex.lineplot_median_replicates_with_grouping,
            ex.lineplot_mean_replicates_with_grouping,
            ex.lineplot_median_replicates_no_grouping,
            ex.lineplot_mean_replicates_no_grouping,
            ex.lineplot_no_replicates_with_grouping,
            ex.lineplot_no_replicates_no_grouping
        ]
    }
)


plugin.visualizers.register_function(
    function=boxplot,
    inputs={},
    parameters={
        'metadata': Metadata,
        'distribution_measure': Str,
        'group_by': Str,
        'whisker_range': Str % Choices('tukeys_iqr', 'percentile', 'minmax'),
        'box_orientation': Str % Choices('horizontal', 'vertical'),
        'title': Str
    },
    name='Boxplot',
    description='Basic boxplot for visualizing a numeric Metadata measure'
                ' grouped by a categorical Metadata measure with choices for'
                ' the whisker range.',
    parameter_descriptions={
        'metadata': 'Any metadata-like input with at least one numeric measure'
                    ' and one categorical measure for visualizing.',
        'distribution_measure': 'The numeric measure that will be used to'
                                ' create each box plot distribution.',
        'group_by': 'The categorical measure that will be used to group the'
                    ' data into separate box plots. If left blank, all data'
                    ' will be represented within a single box.',
        'whisker_range': 'The range that will be used for calculating the'
                         ' whisker lengths for each box. Options are'
                         ' `tukeys_iqr` (1.5 IQR clamped to the data extent),'
                         ' `percentile` (91th/9th percentile), or `minmax`.'
                         ' Any data points that fall outside of the chosen'
                         ' range will be represented as outliers that are'
                         ' plotted as circular points, unless the'
                         ' `suppressOutliers` checkbox has been enabled'
                         ' on the rendered visualization.',
        'box_orientation': 'The visual orientataion of the boxes (either'
                           ' horizontal or vertical).',
        'title': 'The title of the boxplot.'
    }
)
