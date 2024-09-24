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
from ._util import _json_replace, _measure_validation, _col_type_validation


def boxplot(output_dir: str, metadata: Metadata,
            distribution_measure: NumericMetadataColumn,
            whisker_range: str, group_by: CategoricalMetadataColumn = None,
            title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # input validation for distribution & group_by measures
    _col_type_validation(metadata=metadata, measure=distribution_measure,
                         col_type='numeric')
    _measure_validation(metadata=metadata, measure=distribution_measure)

    if group_by:
        _col_type_validation(metadata=metadata, measure=group_by,
                             col_type='categorical')
        _measure_validation(metadata=metadata, measure=group_by)

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/boxplot')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'boxplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    metadata_obj = json.loads(md.to_json(orient='records'))

    # outlier filtering expression pre-processing
    # this needs to be created as an f-string prior to being passed into
    # the vega spec so that the var can be templated in
    # prior to it being read as a string
    expr = (
        f"datum['{distribution_measure}']"
        f" < datum.summary.whiskerLow || datum['{distribution_measure}']"
        " > datum.summary.whiskerHigh"
    )

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              distribution_measure=distribution_measure,
                              whisker_range=whisker_range,
                              group_by=group_by, title=title, expr=expr)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
