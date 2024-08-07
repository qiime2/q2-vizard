# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import json
import pkg_resources
import jinja2

from qiime2 import Metadata, NumericMetadataColumn, CategoricalMetadataColumn
from ._util import _json_replace, _measure_validation


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   color_by_group: CategoricalMetadataColumn = None,
                   title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # handling categorical columns for color grouping
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # validation for group measure
    if color_by_group:
        _measure_validation(metadata=metadata, measure=color_by_group,
                            col_type='categorical')

    # setting default (or selected) group measure for color-coding
    # and adding 'none' for removing color-coding
    md_cols_categorical.append('none')
    if color_by_group:
        group_dropdown_default = color_by_group
    else:
        group_dropdown_default = md_cols_categorical[0]

    # handling numeric columns for x/y plotting
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    if x_measure:
        _measure_validation(metadata=metadata, measure=x_measure,
                            col_type='numeric')
        x_dropdown_default = x_measure
    else:
        x_dropdown_default = md_cols_numeric[0]

    if y_measure:
        _measure_validation(metadata=metadata, measure=y_measure,
                            col_type='numeric')
        y_dropdown_default = y_measure
    else:
        y_dropdown_default = md_cols_numeric[0]

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/scatterplot_2d')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'scatterplot_2d', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    metadata_obj = json.loads(md.to_json(orient='records'))

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              md_cols_numeric=md_cols_numeric,
                              x_dropdown_default=x_dropdown_default,
                              y_dropdown_default=y_dropdown_default,
                              md_cols_categorical=md_cols_categorical,
                              group_dropdown_default=group_dropdown_default,
                              title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
