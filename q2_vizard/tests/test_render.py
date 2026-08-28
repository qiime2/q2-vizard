# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import hashlib
import importlib.resources

from qiime2.sdk import usage
from qiime2.plugin.testing import TestPluginBase

from .._render import _VENDORED_FILES


class TestRenderedVisualizations(TestPluginBase):
    package = 'q2_vizard.tests'

    def setUp(self):
        super().setUp()

        self.assets = importlib.resources.files('q2_vizard') / 'assets'
        self.vendor = self.assets / 'vendor'

    # Helper method to pull all params for each visualizer using its
    # registered usage examples
    def _iter_rendered_visualizations(self):
        for action_name, action in self.plugin.visualizers.items():
            for example_name, example_f in action.examples.items():
                use = usage.ExecutionUsage()
                example_f(use)

                for var in use.render().values():
                    if var.var_type == 'visualization':
                        yield action_name, example_name, var.value

    def test_every_visualizer_has_a_usage_example(self):
        for name, action in self.plugin.visualizers.items():
            with self.subTest(visualizer=name):
                self.assertTrue(
                    action.examples,
                    f'The `{name}` visualizer does not register any usage'
                    ' examples. This is a requirement within `q2-vizard`,'
                    ' ensuring the rendered output of each viz is covered by'
                    ' `test_rendered_visualizations_copy_vendored_assets`.'
                )

    def test_rendered_visualizations_copy_vendored_assets(self):
        for action_name, example_name, viz in \
                self._iter_rendered_visualizations():
            with self.subTest(visualizer=action_name, example=example_name):
                output_dir = os.path.join(
                    self.temp_dir.name, action_name, example_name)
                viz.export_data(output_dir)

                for filename in _VENDORED_FILES:
                    with open(os.path.join(output_dir, filename), 'rb') as fh:
                        self.assertEqual(fh.read(),
                                         (self.vendor / filename).read_bytes())

    def test_templates_use_local_scripts(self):
        for visualization in self.plugin.visualizers.keys():
            with self.subTest(visualization=visualization):
                template = (
                    self.assets / visualization / 'index.html').read_text()

                self.assertIn('src="vega.min.js"', template)
                self.assertIn('src="vega-embed.min.js"', template)
                self.assertNotIn('cdn.jsdelivr.net', template)

    # TODO: whenever the vega version used is updated (and thus the vega embed
    # files are changed) these checksums will fail if they are not also
    # re-calculated and updated. When this takes place, they will need to get
    # updated here AND in the README.md file (same relpath as vega embed files)
    def test_vendored_files_checksums(self):
        expected = {
            'vega.min.js': (
                '731f01b68116bc185a196322096ca342'
                '737424c4995c48a6674f57ebc967e9c1'),
            'vega-embed.min.js': (
                'e5c92904f1b614e54a6a860ecf194ca'
                '88bf948b4faeb7af9a0fe2cad93dc730e'),
        }

        for filename, expected_digest in expected.items():
            with self.subTest(filename=filename):
                digest = hashlib.sha256(
                    (self.vendor / filename).read_bytes()).hexdigest()
                self.assertEqual(digest, expected_digest)
