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

from qiime2 import Metadata
from q2_vizard._util import json_replace


def plot_scatterplot(output_dir: str, data: Metadata, metadata: Metadata,
                     title: str, x_label: str, y_label: str):
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/scatterplot')
    )

    index = J_ENV.get_template('index.html')
    df = data.to_dataframe()
    md = metadata.to_dataframe()

    data = json.loads(df.to_json(orient='records'))
    metadata = json.loads(md.to_json(orient='records'))

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'scatterplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(json_obj, data=data, metadata=metadata,
                             title=title, x_label=x_label, y_label=y_label)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
