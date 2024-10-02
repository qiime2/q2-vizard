# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import os
import json
import pkg_resources
import jinja2

from qiime2 import Metadata, NumericMetadataColumn, CategoricalMetadataColumn
from ._util import _json_replace, _measure_validation, _col_type_validation


def lineplot(output_dir: str, metadata: Metadata,
             x_measure: NumericMetadataColumn,
             y_measure: NumericMetadataColumn,
             replicate_method: str = 'none',
             group_by: CategoricalMetadataColumn = None,
             title: str = None):

    # input handling for initial metadata
    md_ids = metadata.id_header
    md = metadata.to_dataframe().reset_index()

    # column validation for x_measure and y_measure
    for measure in [x_measure, y_measure]:
        _col_type_validation(metadata=metadata, measure=measure,
                             col_type='numeric')
        _measure_validation(metadata=metadata, measure=measure)

    if y_measure == x_measure:
        raise ValueError(f'The same column `{x_measure}` has been used'
                         ' for `x_measure` and `y_measure`.'
                         ' Please choose different columns in your'
                         ' metadata for these measures.')

    # filtering md cols for the y-axis dropdown
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric)

    # column validation for grouping
    if group_by:
        _col_type_validation(metadata=metadata, measure=group_by,
                             col_type='categorical')
        _measure_validation(metadata=metadata, measure=group_by)

    if replicate_method == 'none':
        # handling for md sorting based on the selected group_by measure
        if group_by:
            group_by_ordered_md = []
            for i in md[group_by].unique():
                group_by_md = md[md[group_by] == i].sort_values(x_measure)
                if any(group_by_md[x_measure].duplicated()):
                    raise ValueError(
                        f'Replicates found in `{x_measure}` within the'
                        f' `{i}` `group_by` group. If this is expected,'
                        ' please select a `replicate_method`.'
                        ' If this is not expected, please either filter out'
                        f' replicates from `{x_measure}` or select a different'
                        ' column in your metadata for use in the `x_measure`.')

                group_by_ordered_md.append(group_by_md)
            # this creates md that's grouped by the group_by column and
            # sorted (per unique group_by value) by the x_measure
            # this is what's used to create the scatterplot points
            # line will be overlaid directly on these points since
            # there are no replicates to average
            ordered_md = pd.concat(group_by_ordered_md)
            ordered_md = ordered_md.sort_values(by=[group_by, x_measure])
            # a bit of a hack but two separate tables are passed into vega
            # when we do have replicates, so it's easier to set what we'd
            # expect to be the second table to the ordered_md in this case
            # since we're not handling averages in these branches
            averaged_md = ordered_md

        # x_measure replicate validation & sorting with no group_by measure
        else:
            # this adds a fake column with a single group that's used
            # in vega to render the legend and coloring when there
            # aren't multiple groups to create grouping with
            md['legend'] = 'data'
            group_by = 'legend'

            ordered_md = md.sort_values(x_measure)
            averaged_md = ordered_md

            if any(ordered_md[x_measure].duplicated()):
                raise ValueError(
                    f'Replicates found in `{x_measure}`.'
                    ' If this is expected, please select a `replicate_method`.'
                    ' If this is not expected, please either filter out'
                    f' replicates from `{x_measure}` or select a different'
                    ' column in your metadata for use in the `x_measure`.')

    # replicate handling when True
    elif replicate_method in ['median', 'mean']:

        # handling for md sorting based on the selected group_by measure
        if group_by:
            group_by_ordered_md = []
            for i in md[group_by].unique():
                group_by_md = md[md[group_by] == i].sort_values(x_measure)
                group_by_ordered_md.append(group_by_md)
            # this creates md that's grouped by the group_by column and
            # sorted (per unique group_by value) by the x_measure
            # this is what's used to create the scatterplot points
            ordered_md = pd.concat(group_by_ordered_md)
            ordered_md = ordered_md.sort_values(by=[group_by, x_measure])

        else:
            # this adds a fake column with a single group that's used
            # in vega to render the legend and coloring when there
            # aren't multiple groups to create grouping with
            md['legend'] = 'data'
            group_by = 'legend'

            ordered_md = md.sort_values(x_measure)

        # this creates a subset of the md grouped by the group_by column
        # y values at each unique x are averaged
        # this is used to create the average line
        if replicate_method == 'median':
            averaged_md = \
                (ordered_md.groupby([x_measure, group_by],
                                    as_index=False)[md_cols_numeric].median())
        elif replicate_method == 'mean':
            averaged_md = \
                (ordered_md.groupby([x_measure, group_by],
                                    as_index=False)[md_cols_numeric].mean())

        averaged_md = averaged_md.sort_values(by=[group_by, x_measure])

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/lineplot')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'lineplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    md_obj = json.loads(md.to_json(orient='records'))
    averaged_md_obj = json.loads(averaged_md.to_json(orient='records'))

    if replicate_method in ['median', 'mean']:
        subtitle = f'Data was averaged using the `{replicate_method}` method.'
    else:
        subtitle = ' '

    full_spec = \
        _json_replace(json_obj, metadata=md_obj, md_ids=md_ids,
                      averaged_metadata=averaged_md_obj,
                      md_cols_numeric=md_cols_numeric,
                      x_measure=x_measure, y_measure=y_measure,
                      group_by=group_by, title=title, subtitle=subtitle)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
