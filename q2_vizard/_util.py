# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

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

    # manual check for the rendered stats for boxplot
    def _stats_util(data):
        # Sort the data
        sorted_data = data.sort()

        # Calculate min/max
        minimum = data[0]
        maximum = data[-1]

        # calculate median
        def _calculate_median(sorted_data):
            n = len(sorted_data)
            middle = n // 2

            if n % 2 == 0:
                median = (sorted_data[middle - 1] + sorted_data[middle]) / 2
            else:
                median = sorted_data[middle]
            return median

        # Function to calculate quartiles
        def _calculate_quartiles(sorted_data):
            n = len(sorted_data)
            middle = n // 2

            if n % 2 == 0:
                lower_half = sorted_data[:middle]
                upper_half = sorted_data[middle:]
            else:
                lower_half = sorted_data[:middle]
                upper_half = sorted_data[middle+1:]

            q1 = _calculate_median(lower_half)
            q3 = _calculate_median(upper_half)
            return q1, q3

        # calculate percentiles
        def _calculate_percentile(sorted_data, percentile):
            n = len(sorted_data)
            rank = (percentile / 100) * (n - 1)
            lower_index = int(rank)
            upper_index = lower_index + 1
            weight = rank - lower_index

            if upper_index >= n:
                return sorted_data[lower_index]
            else:
                return (sorted_data[lower_index] * (1 - weight) +
                        sorted_data[upper_index] * weight)

        # Perform calculations
        median = _calculate_median(sorted_data)
        q1, q3 = _calculate_quartiles(sorted_data)
        iqr = q3 - q1

        # Calculate Tukey's fences (lower and upper bounds)
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr

        # Calculate percentiles
        p09 = _calculate_percentile(data, 9)
        p91 = _calculate_percentile(data, 91)

        return (minimum, maximum, median, q1, q3,
                lower_fence, upper_fence, p09, p91)
