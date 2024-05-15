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
from q2_vizard._util import json_replace


def scatterplot_2d(output_dir: str, metadata: Metadata,
                   x_measure: NumericMetadataColumn = None,
                   y_measure: NumericMetadataColumn = None,
                   group_measure: CategoricalMetadataColumn = None,
                   title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # handling categorical columns for color grouping
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # validation for group measure
    if group_measure:
        if group_measure not in metadata.columns:
            raise ValueError(f'"{group_measure}" not found as a column'
                             ' in the Metadata.')
        if group_measure not in md_cols_categorical:
            raise ValueError(f'"{group_measure}" not of type'
                             ' `CategoricalMetadataColumn`.')

    # setting default (or selected) group measure for color-coding
    # and adding 'none' for removing color-coding
    md_cols_categorical.append('none')
    if group_measure:
        md_dropdown_default = group_measure
    else:
        md_dropdown_default = md_cols_categorical[0]

    # handling numeric columns for x/y plotting
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    for measure in [x_measure, y_measure]:
        if measure not in metadata.columns:
            raise ValueError(f'"{measure}" not found as a column'
                             ' in the Metadata.')
        if measure not in md_cols_numeric:
            raise TypeError(f'"{measure}" not of type `NumericMetadataColumn`.'
                            ' Both input measures must contain numeric data.')

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

    full_spec = json_replace(json_obj, metadata=metadata_obj,
                             x_measure=x_measure, y_measure=y_measure,
                             md_cols_categorical=md_cols_categorical,
                             md_dropdown_default=md_dropdown_default,
                             title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
