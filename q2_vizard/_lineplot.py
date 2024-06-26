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

from qiime2 import Metadata, NumericMetadataColumn
from q2_vizard._util import json_replace


def lineplot(output_dir: str, metadata: Metadata,
             x_measure: NumericMetadataColumn = None,
             y_measure: NumericMetadataColumn = None,
             title: str = None):

    # jinja templating & JSON-ifying
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/lineplot')
    )
    index = J_ENV.get_template('index.html')

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'lineplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    metadata_obj = json.loads(md.to_json(orient='records'))

    full_spec = json_replace(json_obj, metadata=metadata_obj,
                             md_cols_numeric=md_cols_numeric,
                             x_dropdown_default=x_dropdown_default,
                             y_dropdown_default=y_dropdown_default,
                             title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
