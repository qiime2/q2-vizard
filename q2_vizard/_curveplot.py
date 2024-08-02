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
from q2_vizard._util import json_replace, measure_validation


def curveplot(output_dir: str, metadata: Metadata,
              x_measure: NumericMetadataColumn,
              y_measure: NumericMetadataColumn = None,
              group: CategoricalMetadataColumn = None,
              color_by: CategoricalMetadataColumn = None,
              title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # handling categorical columns for group & colorBy params
    md_cols_categorical = \
        metadata.filter_columns(column_type='categorical').to_dataframe()
    md_cols_categorical = list(md_cols_categorical.columns)

    # validation for group measure
    if group:
        measure_validation(metadata=metadata, measure=group,
                           col_type='categorical')

    # validation for colorBy measure
    if color_by:
        measure_validation(metadata=metadata, measure=color_by,
                           col_type='categorical')

    # setting default (or selected) group measure for color-coding
    # and adding 'none' for removing color-coding
    md_cols_categorical.append('none')
    if color_by:
        colorby_dropdown_default = color_by
    else:
        colorby_dropdown_default = md_cols_categorical[0]

    # handling numeric columns for x/y plotting
    md_cols_numeric = \
        metadata.filter_columns(column_type='numeric').to_dataframe()
    md_cols_numeric = list(md_cols_numeric.columns)

    # validation for x/y measures
    if x_measure:
        measure_validation(metadata=metadata, measure=x_measure,
                           col_type='numeric')

    if y_measure:
        measure_validation(metadata=metadata, measure=y_measure,
                           col_type='numeric')
        y_dropdown_default = y_measure
    else:
        y_dropdown_default = md_cols_numeric[0]

    # TODO: add handling for x & y(x), disallowing replicate data & ordering X

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/curveplot')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'curveplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    metadata_obj = json.loads(md.to_json(orient='records'))

    full_spec = json_replace(json_obj, metadata=metadata_obj,
                             md_cols_numeric=md_cols_numeric,
                             y_dropdown_default=y_dropdown_default,
                             md_cols_categorical=md_cols_categorical,
                             colorby_dropdown_default=colorby_dropdown_default,
                             title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
