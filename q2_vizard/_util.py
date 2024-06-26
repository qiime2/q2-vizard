# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

def json_replace(json_obj, **values):
    """
    Search for elements of `{"{{REPLACE_PARAM}}": "some_key"}` and replace
    with the result of `values["some_key"]`.
    """
    if type(json_obj) is dict and list(json_obj) == ["{{REPLACE_PARAM}}"]:
        param_name = json_obj["{{REPLACE_PARAM}}"]
        return values[param_name]

    if type(json_obj) is list:
        return [json_replace(x, **values) for x in json_obj]

    elif type(json_obj) is dict:
        return {key: json_replace(value, **values)
                for key, value in json_obj.items()}

    else:
        return json_obj


def measure_validation(metadata, measure, col_type):
    if col_type == 'categorical':
        md_type = 'CategoricalMetadataColumn'
    elif col_type == 'numeric':
        md_type = 'NumericMetadataColumn'
    else:
        raise TypeError('Invalid column type provided. Must be `categorical`'
                        ' or `numeric`.')

    if measure not in metadata.columns:
        raise ValueError(f'`{measure}` not found as a column in the Metadata.')

    valid_columns_md = \
        metadata.filter_columns(column_type=col_type).to_dataframe()
    valid_columns_list = list(valid_columns_md.columns)

    if measure not in valid_columns_list:
        raise TypeError(f'`{measure}` not of type `{md_type}`.')
