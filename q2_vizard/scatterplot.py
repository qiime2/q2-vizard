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


def _scatterplot_prep(metadata, x_measure, y_measure, color_by):
    # input handling for initial metadata
    md_ids = metadata.id_header
    md = metadata.to_dataframe().reset_index()
    md['legendDefault'] = 'data'

    # measure validation for x/y & color_by
    if color_by:
        _measure_validation(metadata=metadata, measure=color_by)

    for measure in (x_measure, y_measure):
        if measure:
            _measure_validation(metadata=metadata, measure=measure)
            _col_type_validation(metadata=metadata, measure=measure,
                                 col_type='numeric')

    # handling numeric columns for x/y plotting
    # numeric cols left as df for scatterplot_correlation
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()

    # handling categorical columns for color grouping
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # every column is available for color-coding, plus 'legendDefault'
    md_cols_color = (md_cols_categorical + list(md_cols_numeric.columns)
                     + ['legendDefault'])

    metadata_obj = json.loads(md.to_json(orient='records'))

    return (metadata_obj, md_ids, md_cols_numeric,
            md_cols_categorical, md_cols_color)


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   color_by: MetadataColumn = None,
                   discrete_color_palette: str = None,
                   continuous_color_palette: str = None,
                   title: str = None):

    (metadata_obj, md_ids, md_cols_numeric,
     md_cols_categorical, md_cols_color) = \
        _scatterplot_prep(metadata=metadata, x_measure=x_measure,
                          y_measure=y_measure, color_by=color_by)

    md_cols_numeric = list(md_cols_numeric.columns)

    if discrete_color_palette and continuous_color_palette:
        raise ValueError('Only one of `discrete_color_palette` and'
                         ' `continuous_color_palette` can be chosen.')

    group_dropdown_default = color_by or 'legendDefault'
    # validation for group measure & selected colorPalette
    if color_by:
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

    # set dropdowns for x/y measures
    x_dropdown_default = x_measure or md_cols_numeric[0]
    y_dropdown_default = y_measure or md_cols_numeric[0]

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


def scatterplot_correlation(output_dir: str, metadata: Metadata,
                            x_measure: NumericMetadataColumn = None,
                            y_measure: NumericMetadataColumn = None,
                            color_by: MetadataColumn = None,
                            title: str = None):

    (metadata_obj, md_ids, md_cols_numeric, _, md_cols_color) = \
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
                         ' scatterplot without xy bounds, try using'
                         ' `scatterplot_2d`.')

    # after iterating all we want is the cols from here
    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    if x_measure and x_measure not in md_cols_numeric_in_range:
        raise ValueError(f'{x_measure} values not bounded within range'
                         ' [-1, 1]. `scatterplot_correlation` is intended'
                         ' for use with data in these bounds. For a more'
                         ' flexible scatterplot without xy bounds, try'
                         ' using `scatterplot_2d`.')

    if y_measure and y_measure not in md_cols_numeric_in_range:
        raise ValueError(f'{y_measure} values not bounded within range'
                         ' [-1, 1]. `scatterplot_correlation` is intended'
                         ' for use with data in these bounds. For a more'
                         ' flexible scatterplot without xy bounds, try'
                         ' using `scatterplot_2d`.')

    # set dropdown defaults
    x_dropdown_default = x_measure or md_cols_numeric_in_range[0]
    y_dropdown_default = y_measure or md_cols_numeric_in_range[0]
    group_dropdown_default = color_by or 'legendDefault'

    _render_visualization(output_dir, 'scatterplot_correlation', 'spec.json',
                          metadata=metadata_obj, md_ids=md_ids,
                          md_cols_numeric=md_cols_numeric,
                          md_cols_numeric_in_range=md_cols_numeric_in_range,
                          x_dropdown_default=x_dropdown_default,
                          y_dropdown_default=y_dropdown_default,
                          md_cols_color=md_cols_color,
                          group_dropdown_default=group_dropdown_default,
                          title=title)
