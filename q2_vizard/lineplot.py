# ----------------------------------------------------------------------------
# Copyright (c) 2023-2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import os
import json
import pkg_resources
import jinja2

from qiime2 import Metadata, NumericMetadataColumn, CategoricalMetadataColumn
from ._util import _json_replace, _measure_validation


def lineplot(output_dir: str, metadata: Metadata,
             x_measure: NumericMetadataColumn,
             y_measure: NumericMetadataColumn,
             replicates: bool = False,
             average: str = None,
             facet_by: CategoricalMetadataColumn = None,
             title: str = None):

    # input handling for initial metadata
    md = metadata.to_dataframe()

    # column validation for x_measure and y_measure
    _measure_validation(metadata=metadata, measure=x_measure,
                        col_type='numeric')

    _measure_validation(metadata=metadata, measure=y_measure,
                        col_type='numeric')

    if y_measure == x_measure:
        raise ValueError(f'The same column `{x_measure}` has been used for'
                         ' `x_measure` and `y_measure`.'
                         ' Please choose different columns in your'
                         ' metadata for these measures.')

    # replicate handling when set to false
    if not replicates:
        # handling for metadata sorting based on the selected facet_by measure
        if facet_by:
            _measure_validation(metadata=metadata, measure=facet_by,
                                col_type='categorical')
            facet_by_ordered_md = []

            for i in md[facet_by].unique():
                facet_byed_md = md[md[facet_by] == i].sort_values(x_measure)
                if any(facet_byed_md[x_measure].duplicated()):
                    raise ValueError(
                        f'Replicates found in `{x_measure}` within the `{i}`'
                        f' `facet_by`. If this is expected, please set'
                        ' `replicates` to True and select an `average` method.'
                        ' If this is not expected, please either filter out'
                        f' replicates from `{x_measure}` or select a different'
                        ' column in your metadata for use in the `x_measure`.')

                facet_by_ordered_md.append(facet_byed_md)
            ordered_md = pd.concat(facet_by_ordered_md)

        else:
            # x_measure replicate validation & sorting with no facet_by measure
            ordered_md = md.sort_values(x_measure)
            if any(ordered_md[x_measure].duplicated()):
                raise ValueError(
                    f'Replicates found in `{x_measure}`.'
                    ' If this is expected, please set `replicates` to True'
                    ' and select an `average` method.'
                    ' If this is not expected, please either filter out'
                    f' replicates from {x_measure} or select a different'
                    ' column in your metadata for use in the `x_measure`.')
    # replicate handling when set to true
    else:
        pass

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

    metadata_obj = json.loads(ordered_md.to_json(orient='records'))

    full_spec = _json_replace(json_obj, metadata=metadata_obj,
                              x_measure=x_measure, y_measure=y_measure,
                              facet_by=facet_by, title=title)

    with open(os.path.join(output_dir, 'index.html'), 'w') as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
