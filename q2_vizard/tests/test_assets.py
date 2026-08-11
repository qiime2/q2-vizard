# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import hashlib
import importlib.resources
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from qiime2 import Metadata

from .._util import _VENDORED_FILES
from ..boxplot import boxplot
from ..heatmap import heatmap
from ..lineplot import lineplot
from ..scatterplot import scatterplot_2d


class TestVendoredAssets(unittest.TestCase):
    def setUp(self):
        index = pd.Index(['sample1', 'sample2', 'sample3'],
                         name='sample-id')
        data = [
            [1.0, 'foo'],
            [2.0, 'bar'],
            [3.0, 'baz'],
        ]
        self.md = Metadata(pd.DataFrame(
            data=data, index=index, dtype=object,
            columns=['numeric-col', 'categorical-col']))
        self.assets = importlib.resources.files('q2_vizard') / 'assets'
        self.vendor = self.assets / 'vendor'

    def test_visualizations_copy_vendored_assets(self):
        visualizers = {
            'scatterplot_2d': lambda output_dir: scatterplot_2d(
                output_dir, self.md),
            'heatmap': lambda output_dir: heatmap(
                output_dir, self.md, 'categorical-col', 'categorical-col',
                'numeric-col'),
            'lineplot': lambda output_dir: lineplot(
                output_dir, self.md, 'numeric-col'),
            'boxplot': lambda output_dir: boxplot(
                output_dir, self.md, 'numeric-col', 'categorical-col'),
        }

        for visualization, render in visualizers.items():
            with self.subTest(visualization=visualization), \
                    tempfile.TemporaryDirectory() as output_dir:
                render(output_dir)

                for filename in _VENDORED_FILES:
                    packaged = (self.vendor / filename).read_bytes()
                    with open(Path(output_dir) / filename, 'rb') as fh:
                        emitted = fh.read()

                    self.assertEqual(emitted, packaged)

    def test_templates_use_local_scripts(self):
        for visualization in (
                'scatterplot_2d', 'heatmap', 'lineplot', 'boxplot'):
            with self.subTest(visualization=visualization):
                template = (
                    self.assets / visualization / 'index.html').read_text()

                self.assertIn('src="vega.min.js"', template)
                self.assertIn('src="vega-embed.min.js"', template)
                self.assertNotIn('cdn.jsdelivr.net', template)

    def test_vendored_script_checksums(self):
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
