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
from ._util import _json_replace, _measure_validation


def boxplot(output_dir: str, metadata: Metadata,
            distribution: NumericMetadataColumn, whisker_range: str,
            facet_by: CategoricalMetadataColumn = None,
            average_method: str = 'median', title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe().reset_index()

    # input validation for distribution & facet_by measures
    _measure_validation(metadata=metadata, measure=distribution,
                        col_type='numeric')
    if facet_by:
        _measure_validation(metadata=metadata, measure=facet_by,
                            col_type='categorical')

# TODO: more pre-processing for box plot stats

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

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              distribution=distribution, facet_by=facet_by,
                              average_method=average_method, title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
