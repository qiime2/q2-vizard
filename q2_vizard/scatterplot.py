# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from qiime2 import Metadata, NumericMetadataColumn, MetadataColumn

from ._util import _col_type_validation, _measure_validation
from ._render import _render_visualization


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   color_by: MetadataColumn = None,
                   title: str = None):

    # input handling for initial metadata
    md_ids = metadata.id_header
    md = metadata.to_dataframe().reset_index()
    md['legendDefault'] = 'data'

    # handling categorical columns for color grouping
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # validation for group measure - both categorical & numeric columns
    # are valid for color-coding, so only the column name is validated
    if color_by:
        _measure_validation(metadata=metadata, measure=color_by)

    # setting default (or selected) group measure for color-coding
    if color_by:
        group_dropdown_default = color_by
    else:
        group_dropdown_default = 'legendDefault'

    # handling numeric columns for x/y plotting
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric.columns)

    # every column is available for color-coding, with 'legendDefault'
    # included for removing color-coding
    md_cols_color = md_cols_categorical + md_cols_numeric + ['legendDefault']

    # validation for x/y measures
    if x_measure:
        _measure_validation(metadata=metadata, measure=x_measure)
        _col_type_validation(metadata=metadata, measure=x_measure,
                             col_type='numeric')
        x_dropdown_default = x_measure
    else:
        x_dropdown_default = md_cols_numeric[0]

    if y_measure:
        _measure_validation(metadata=metadata, measure=y_measure)
        _col_type_validation(metadata=metadata, measure=y_measure,
                             col_type='numeric')
        y_dropdown_default = y_measure
    else:
        y_dropdown_default = md_cols_numeric[0]

    metadata_obj = json.loads(md.to_json(orient='records'))

    _render_visualization(output_dir, 'scatterplot_2d', 'spec.json',
                          metadata=metadata_obj, md_ids=md_ids,
                          md_cols_numeric=md_cols_numeric,
                          x_dropdown_default=x_dropdown_default,
                          y_dropdown_default=y_dropdown_default,
                          md_cols_color=md_cols_color,
                          group_dropdown_default=group_dropdown_default,
                          title=title)
