import os
import json
import pkg_resources

import pandas as pd
import jinja2

from q2_vizard._util import json_replace


def plot_heatmap(output_dir: str, data: pd.DataFrame):
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets')
    )
    index = J_ENV.get_template('index.html')

    measure = data['measure'].attrs['title']
    data = json.loads(data.to_json(orient='records'))

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'spec.json')
    )

    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(json_obj, data=data, measure=measure, title='vizard', x_label='group', y_label='subject')

    with open(os.path.join(output_dir, "index.html"), "w") as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))