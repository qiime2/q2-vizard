# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import os
import pkg_resources
import jinja2
import json
from collections import Counter

from q2_vizard._util import json_replace


def plot_heatmap(output_dir: str, data: pd.DataFrame, x_label: str, 
                 y_label: str, gradient: str):
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/heatmap')
    )
    # general viz
    x_label_name = data[x_label].attrs['title']
    measure_name = data[gradient].attrs['title']
    y_label_name = data[y_label].attrs['title']
    # orientation parameter could switch this 
    title = f'{measure_name} of {y_label_name} across {x_label_name}'

    index = J_ENV.get_template('index.html')
    data = json.loads(data.to_json(orient='records'))
    # change index.html and spec.json to be more specific thanks :)
    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'heatmap', 'heatmap_spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(json_obj, data=data, x_label=x_label, 
                             x_label_name=x_label_name,
                             y_label=y_label, y_label_name=y_label_name,
                             title=title, measure=gradient, 
                             measure_name=measure_name)

    with open(os.path.join(output_dir, "index.html"), "w") as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))

