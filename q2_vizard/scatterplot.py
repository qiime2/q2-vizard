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


def _scatterplot_prep(metadata, x_measure, y_measure, color_by):

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

    # every column is available for color-coding, with 'legendDefault'
    # included for removing color-coding
    md_cols_color = (md_cols_categorical + list(md_cols_numeric.columns)
                     + ['legendDefault'])

    for measure in (x_measure, y_measure):
        if measure:
            _measure_validation(metadata=metadata, measure=measure)
            _col_type_validation(metadata=metadata, measure=measure,
                                 col_type='numeric')

    metadata_obj = json.loads(md.to_json(orient='records'))

    return (metadata_obj, md_ids, md_cols_numeric, md_cols_color,
            group_dropdown_default)


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   color_by: MetadataColumn = None,
                   title: str = None):

    (metadata_obj, md_ids, md_cols_numeric, md_cols_color,
     group_dropdown_default) = \
        _scatterplot_prep(metadata=metadata, x_measure=x_measure,
                          y_measure=y_measure, color_by=color_by)

    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    if not x_measure:
        x_dropdown_default = md_cols_numeric[0]
    else:
        x_dropdown_default = x_measure

    if not y_measure:
        y_dropdown_default = md_cols_numeric[0]
    else:
        y_dropdown_default = y_measure

    _render_visualization(output_dir, 'scatterplot_2d', 'spec.json',
                          metadata=metadata_obj, md_ids=md_ids,
                          md_cols_numeric=md_cols_numeric,
                          x_dropdown_default=x_dropdown_default,
                          y_dropdown_default=y_dropdown_default,
                          md_cols_color=md_cols_color,
                          group_dropdown_default=group_dropdown_default,
                          title=title)


def scatterplot_correlation(output_dir: str, metadata: Metadata,
                            x_measure: NumericMetadataColumn = None,
                            y_measure: NumericMetadataColumn = None,
                            color_by: MetadataColumn = None,
                            title: str = None):

    (metadata_obj, md_ids, md_cols_numeric, md_cols_color,
     group_dropdown_default) = \
        _scatterplot_prep(metadata=metadata, x_measure=x_measure,
                          y_measure=y_measure, color_by=color_by)

    md_cols_numeric_in_range = []
    for col, vals in md_cols_numeric.items():
        if vals.between(-1, 1).all():
            md_cols_numeric_in_range.append(col)

    if len(md_cols_numeric_in_range) == 0:
        raise ValueError('None of the numeric columns in your metadata have'
                         ' values that remain within range [-1, 1].'
                         ' `scatterplot_correlation` is intended for use with'
                         ' data in these bounds. For a more flexible'
                         ' scatterplot without xy bounds, try using' \
                         ' `scatterplot_2d`.')

    # after iterating all we want is the cols from here
    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    if x_measure:
        if x_measure not in md_cols_numeric_in_range:
            raise ValueError(f'{x_measure} values not bounded within range'
                             ' [-1, 1]. `scatterplot_correlation` is intended'
                             ' for use with data in these bounds. For a more'
                             ' flexible scatterplot without xy bounds, try'
                             ' using `scatterplot_2d`.')
        x_dropdown_default = x_measure
    else:
        x_dropdown_default = md_cols_numeric_in_range[0]

    if y_measure:
        if y_measure not in md_cols_numeric_in_range:
            raise ValueError(f'{y_measure} values not bounded within range'
                             ' [-1, 1]. `scatterplot_correlation` is intended'
                             ' for use with data in these bounds. For a more'
                             ' flexible scatterplot without xy bounds, try'
                             ' using `scatterplot_2d`.')
        y_dropdown_default = y_measure
    else:
        y_dropdown_default = md_cols_numeric_in_range[0]

    _render_visualization(output_dir, 'scatterplot_correlation', 'spec.json',
                          metadata=metadata_obj, md_ids=md_ids,
                          md_cols_numeric=md_cols_numeric,
                          md_cols_numeric_in_range=md_cols_numeric_in_range,
                          x_dropdown_default=x_dropdown_default,
                          y_dropdown_default=y_dropdown_default,
                          md_cols_color=md_cols_color,
                          group_dropdown_default=group_dropdown_default,
                          title=title)
