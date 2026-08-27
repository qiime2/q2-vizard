# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from qiime2 import Metadata, MetadataColumn, NumericMetadataColumn

from ._util import _col_type_validation, _measure_validation
from ._render import _render_visualization


def heatmap(output_dir: str, metadata: Metadata,
            x_measure: MetadataColumn,
            y_measure: MetadataColumn,
            gradient_measure: NumericMetadataColumn,
            title: str = None):

    # input handling for initial metadata
    md_ids = metadata.id_header
    md = metadata.to_dataframe().reset_index()

    # md validation for all input measures
    for measure in [x_measure, y_measure, gradient_measure]:
        _measure_validation(metadata=metadata, measure=measure)

    # col type validation for gradient_measure
    _col_type_validation(metadata=metadata,
                         measure=gradient_measure,
                         col_type='numeric')

    metadata_obj = json.loads(md.to_json(orient='records'))

    _render_visualization(output_dir, 'heatmap', 'spec.json',
                          metadata=metadata_obj, md_ids=md_ids,
                          x_measure=x_measure, y_measure=y_measure,
                          gradient_measure=gradient_measure, title=title)
