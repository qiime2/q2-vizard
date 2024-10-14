# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import numpy as np


def _json_replace(json_obj, **values):
    """
    Search for elements of `{"{{REPLACE_PARAM}}": "some_key"}` and replace
    with the result of `values["some_key"]`.
    """
    if type(json_obj) is dict and list(json_obj) == ["{{REPLACE_PARAM}}"]:
        param_name = json_obj["{{REPLACE_PARAM}}"]
        return values[param_name]

    if type(json_obj) is list:
        return [_json_replace(x, **values) for x in json_obj]

    elif type(json_obj) is dict:
        return {key: _json_replace(value, **values)
                for key, value in json_obj.items()}

    else:
        return json_obj


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


# manual checks for the rendered stats in boxplot
def _calculate_median(sorted_values):
    n = len(sorted_values)
    middle = n // 2

    if n % 2 == 0:
        median = (sorted_values.iloc[middle - 1] +
                  sorted_values.iloc[middle]) / 2.0
    else:
        median = sorted_values.iloc[middle]
    return median


def _calculate_quartiles(sorted_values):
    q1 = np.percentile(sorted_values, 25, interpolation='linear')
    q3 = np.percentile(sorted_values, 75, interpolation='linear')
    return q1, q3


def _calculate_percentile(sorted_values, percentile):
    n = len(sorted_values)
    rank = (percentile / 100) * (n - 1)

    lower_index = int(rank)
    upper_index = min(lower_index + 1, n - 1)

    weight = rank - lower_index

    lower_value = sorted_values.iloc[lower_index]
    upper_value = sorted_values.iloc[upper_index]

    percentile_value = lower_value * (1 - weight) + upper_value * weight

    return percentile_value
