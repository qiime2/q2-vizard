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


# scatterplot examples
def scatterplot_defaults(use):
    metadata = use.init_metadata('metadata', md_factory)

    scatterplot_viz, = use.action(
        use.UsageAction('vizard', 'scatterplot_2d'),
        use.UsageInputs(
            metadata=metadata
        ),
        use.UsageOutputNames(
            visualization='scatterplot'
        )
    )


def scatterplot_all_measures(use):
    metadata = use.init_metadata('metadata', md_factory)

    scatterplot_viz, = use.action(
        use.UsageAction('vizard', 'scatterplot_2d'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            color_by='group',
        ),
        use.UsageOutputNames(
            visualization='scatterplot'
        )
    )


# lineplot examples
def lineplot_median_replicates_with_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            group_by='group',
            replicate_method='median',
            title='Lineplot with median replicate method, grouped by `group`.'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


def lineplot_mean_replicates_with_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            group_by='group',
            replicate_method='mean',
            title='Lineplot with mean replicate method, grouped by `group`.'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


def lineplot_median_replicates_no_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            replicate_method='median',
            title='Lineplot with median replicate method (no grouping).'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


def lineplot_mean_replicates_no_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            replicate_method='mean',
            title='Lineplot with mean replicate method (no grouping).'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


def lineplot_no_replicates_with_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='a',
            y_measure='y',
            group_by='group',
            title='Lineplot with no replicate method, grouped by `group`.'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


def lineplot_no_replicates_no_grouping(use):
    metadata = use.init_metadata('metadata', md_factory)

    lineplot_viz, = use.action(
        use.UsageAction('vizard', 'lineplot'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='b',
            y_measure='y',
            title='Lineplot with no replicate method (no grouping).'
        ),
        use.UsageOutputNames(
            visualization='lineplot'
        )
    )


# heatmap examples
def heatmap(use):
    metadata = use.init_metadata('metadata', md_factory)

    heatmap_viz, = use.action(
        use.UsageAction('vizard', 'heatmap'),
        use.UsageInputs(
            metadata=metadata,
            x_measure='x',
            y_measure='y',
            gradient_measure='a',
        ),
        use.UsageOutputNames(
            visualization='heatmap'
        )
    )
