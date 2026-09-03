# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def _col_type_validation(metadata, measure, col_type):
    if col_type == 'categorical':
        md_type = 'CategoricalMetadataColumn'
    elif col_type == 'numeric':
        md_type = 'NumericMetadataColumn'
    else:
        raise TypeError('Invalid column type provided. Must be `categorical`'
                        ' or `numeric`.')

    valid_columns_md = \
        metadata.filter_columns(column_type=col_type).to_dataframe()
    valid_columns_list = list(valid_columns_md.columns)

    if measure not in valid_columns_list:
        raise TypeError(f'`{measure}` not of type `{md_type}`.')


def _measure_validation(metadata, measure):
    # All of these characters will break the rendered Vega spec when used
    # in the context of a column name, so we're just not going to allow them.
    # This is easier and more transparent than removing these characters and
    # providing a user with a rendered Vega spec with modified column name(s).
    disallowed_chars = ['[]', '[', ']', '.', '\\', "'", '"']

    if measure not in metadata.columns:
        raise ValueError(f'`{measure}` not found as a column in the Metadata.')

    for char in disallowed_chars:
        if char in measure:
            raise ValueError(
                f'Metadata column: `{measure}` contains `{char}`, which cannot'
                f' be parsed by this visualization. Please remove `{char}`'
                ' from this Metadata column name.'
            )
