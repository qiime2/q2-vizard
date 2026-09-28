# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from qiime2 import Metadata, NumericMetadataColumn, MetadataColumn

from ._util import (_col_type_validation, _measure_validation,
                    _DISCRETE_COLOR_PALETTES, _CONTINUOUS_COLOR_PALETTES)
from ._render import _render_visualization


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   color_by: MetadataColumn = None,
                   discrete_color_palette: str = None,
                   continuous_color_palette: str = None,
                   title: str = None):

    # input handling for initial metadata
    md_ids = metadata.id_header
    md = metadata.to_dataframe().reset_index()
    md['legendDefault'] = 'data'

    # handling categorical columns for color grouping
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # handling numeric columns for x/y plotting
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric.columns)

    if discrete_color_palette and continuous_color_palette:
        raise ValueError('Only one of `discrete_color_palette` and'
                         ' `continuous_color_palette` can be chosen.')

    # validation for group measure - both categorical & numeric columns
    # are valid for color-coding, so only the column name is validated
    group_dropdown_default = 'legendDefault'
    if color_by:
        _measure_validation(metadata=metadata, measure=color_by)
        # setting default (or selected) group measure for color-coding
        group_dropdown_default = color_by
        is_categorical = color_by in md_cols_categorical

        # categorical measure with continuous color palette
        if is_categorical and continuous_color_palette is not None:
            raise ValueError('The selected `color_by` measure contains'
                             ' discrete values, but a palette was chosen from'
                             ' the `continuous_color_palette` scale.'
                             ' Please choose a compatible continuous measure,'
                             ' or change your color palette selection'
                             ' to one from `discrete_color_palette`.')
        # numeric measure with discrete color palette
        if not is_categorical and discrete_color_palette is not None:
            raise ValueError('The selected `color_by` measure contains'
                             ' continuous values, but a palette was chosen'
                             ' from the `discrete_color_palette` scale.'
                             ' Please choose a compatible discrete measure, or'
                             ' change your color palette selection to one from'
                             ' `continuous_color_palette`.')

    else:
        if discrete_color_palette is not None:
            if not md_cols_categorical:
                raise ValueError('A `discrete_color_palette` was chosen but'
                                 ' there are no categorical metadata columns'
                                 ' present in the data.')
            group_dropdown_default = md_cols_categorical[0]
        if continuous_color_palette is not None:
            group_dropdown_default = md_cols_numeric[0]

    discrete_selection = discrete_color_palette or 'category10'
    continuous_selection = continuous_color_palette or 'Viridis'

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
                          discrete_selection=discrete_selection,
                          continuous_selection=continuous_selection,
                          discrete_color_palettes=_DISCRETE_COLOR_PALETTES,
                          continuous_color_palettes=_CONTINUOUS_COLOR_PALETTES,
                          title=title)
