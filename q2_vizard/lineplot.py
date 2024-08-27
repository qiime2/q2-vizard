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
from ._util import _json_replace, _measure_validation


def lineplot(output_dir: str, metadata: Metadata,
              x_measure: NumericMetadataColumn,
              y_measure: NumericMetadataColumn = None,
              group: CategoricalMetadataColumn = None,
              title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe()

    # column validation for x_measure
    _measure_validation(metadata=metadata, measure=x_measure,
                        col_type='numeric')

    # handling numeric columns for y(x) measure
    # note that x_measure gets removed because we don't need to plot
    # x against x(x)
    filtered_md_numeric_cols = metadata.filter_columns(
        column_type='numeric').to_dataframe().drop(columns=x_measure)
    md_cols_numeric = list(filtered_md_numeric_cols.columns)

    # column validation for y(x) measure & setting dropdown default
    if y_measure:
        _measure_validation(metadata=metadata, measure=y_measure,
                            col_type='numeric')

        if y_measure == x_measure:
            raise ValueError(f'The same column `{x_measure}` has been used for'
                             ' `x_measure` and `y_measure`.'
                             ' Please choose different columns in your'
                             ' metadata for these measures.')

        y_dropdown_default = y_measure
    else:
        y_dropdown_default = md_cols_numeric[0]

    # handling for metadata sorting based on the selected group measure
    if group:
        _measure_validation(metadata=metadata, measure=group,
                            col_type='categorical')
        group_ordered_md = []

        for i in md[group].unique():
            grouped_md = md[md[group] == i].sort_values(x_measure)
            if any(grouped_md[x_measure].duplicated()):
                raise ValueError(f'Replicates found in `{x_measure}` within'
                                 f' the `{i}` group. Please filter your'
                                 ' metadata to remove replicates from your'
                                 ' selected `x_measure` in the chosen `group`:'
                                 f' `{group}`.')

            group_ordered_md.append(grouped_md)
        ordered_md = pd.concat(group_ordered_md)

    else:
        # x_measure replicate validation & sorting with no group measure
        ordered_md = md.sort_values(x_measure)
        if any(ordered_md[x_measure].duplicated()):
            raise ValueError(f'Replicates found in `{x_measure}`.'
                             ' Please filter your metadata to remove'
                             ' replicates from your selected `x_measure`.')

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

    metadata_obj = json.loads(ordered_md.to_json(orient='records'))

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              x_measure=x_measure, group=group,
                              md_cols_numeric=md_cols_numeric,
                              y_dropdown_default=y_dropdown_default,
                              title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
