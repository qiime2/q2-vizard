# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
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


def scatterplot(output_dir: str, metadata: Metadata,
                x_measure: NumericMetadataColumn,
                y_measure: NumericMetadataColumn,
                title: str = None):

    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/scatterplot')
    )

    index = J_ENV.get_template('index.html')
    md = metadata.to_dataframe()
    md_cols = md.columns

    metadata = json.loads(md.to_json(orient='records'))

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'scatterplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(json_obj, metadata=metadata, x_measure=x_measure,
                             y_measure=y_measure, md_cols=md_cols, title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
