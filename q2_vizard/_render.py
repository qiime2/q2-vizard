# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import importlib.resources
import json
import os
import shutil

import jinja2


_VENDORED_FILES = (
    'vega.min.js',
    'vega-embed.min.js',
    'LICENSE-vega',
    'LICENSE-vega-embed',
)


def _copy_vendored_assets(output_dir):
    vendor_dir = importlib.resources.files(
        'q2_vizard') / 'assets' / 'vendor'

    for filename in _VENDORED_FILES:
        source = vendor_dir / filename
        destination = os.path.join(output_dir, filename)

        with source.open('rb') as source_fh, \
                open(destination, 'wb') as dest_fh:
            shutil.copyfileobj(source_fh, dest_fh)


def _json_replace(json_obj, /, **values):
    """
    Search for elements of `{"{{REPLACE_PARAM}}": "some_key"}` and replace
    with the result of `values["some_key"]`.
    Expects positional args for json_obj so as to avoid any future
    namespace collisions that may appear in the values dict
    """
    if type(json_obj) is dict and list(json_obj) == ["{{REPLACE_PARAM}}"]:
        param_name = json_obj["{{REPLACE_PARAM}}"]
        return values[param_name]

    if type(json_obj) is list:
        return [_json_replace(x, **values) for x in json_obj]

    elif type(json_obj) is dict:
        return {key: _json_replace(value, **values)
                for key, value in json_obj.items()}

    else:
        return json_obj


def _render_visualization(output_dir, name, spec_filename='spec.json', /,
                          **spec_params):
    """
    Base template for rendering all visualizations.
    Expects positional args for output_dir, name & spec_filename
    so as to avoid any future namespace collisions
    that may appear in the spec_params dict.

    Assumes the same general file structure for each viz as shown below:

    per-viz assets
    --------------
    `q2_vizard/assets/{viz_name}`

    index.html
    ----------
    `q2_vizard/assets/{viz_name}/index.html`

    spec(s)
    -------
    `q2_vizard/assets/{viz_name}/{spec_name}.json`
    """
    assets = importlib.resources.files('q2_vizard') / 'assets' / name

    with (assets / spec_filename).open() as fh:
        full_spec = _json_replace(json.load(fh), **spec_params)

    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', f'assets/{name}')
    )
    index = J_ENV.get_template('index.html')

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))

    _copy_vendored_assets(output_dir)
