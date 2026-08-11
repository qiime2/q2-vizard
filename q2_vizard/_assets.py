# ----------------------------------------------------------------------------
# Copyright (c) 2023-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib.resources
import os
import shutil


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
