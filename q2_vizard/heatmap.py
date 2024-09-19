# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import jinja2
import json
import pkg_resources

from qiime2 import Metadata, MetadataColumn, NumericMetadataColumn

from ._util import _json_replace, _col_type_validation, _measure_validation


def heatmap(output_dir: str, metadata: Metadata,
            x_measure: MetadataColumn,
            y_measure: MetadataColumn,
            gradient_measure: NumericMetadataColumn,
            title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # md validation for all input measures
    for measure in [x_measure, y_measure, gradient_measure]:
        _measure_validation(metadata=metadata, measure=measure)

    # col type validation for gradient_measure
    _col_type_validation(metadata=metadata,
                         measure=gradient_measure,
                         col_type='numeric')

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/heatmap')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'heatmap', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    metadata_obj = json.loads(md.to_json(orient='records'))

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              x_measure=x_measure, y_measure=y_measure,
                              gradient_measure=gradient_measure, title=title)

    with open(os.path.join(output_dir, "index.html"), "w") as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
