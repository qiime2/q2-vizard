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

# qiime sample-classifier scatterplot
#   Scatterplot with regression line and regression stats at bottom
#   Currently in seaborn
#   Inputs:
#       --i-predictions SampleData[RegressorPredictions]
#       --m-truth-file Metadata
#       --m-truth-column MetadataColumn[Numeric]
# Metadata column (true values) to plot on x axis
#       --p-missing-samples Choices('error', 'ignore')
# what to do when samples are missing
#
# qiime diversity beta-correlation
#   Scatterplot with mantel test results above it
#   Currently in seaborn
#   Inputs:
#       --i-distance-matrix DistanceMatrix
# matrix of distances between pairs of samples
#       --m-metadata-file Metadata
#       --m-metadata-column MetadataColumn[Numeric]
# numeric column from which to compute pairwise Euclidean dists
#       --p-method Choices('spearman', 'pearson')
# the correlation test to be applied in the mantel test
#       --p-permutations Int Range(0, None)
#       --p-intersect-ids/no-intersect-ids
# if supplied IDs not found in both matrices will be discarded otherwise error
#       --p-label1
# label for `distance-matrix` in output viz
#       --p-label2
# label for `metadata-distance-matrix` in output viz
#
# qiime composition ancon
#   Volcano plot with ancom statistical results
#   and percentile abundances of features by group at bottom
#   Currently in vega
#   Inputs:
#       --i-table FeatureTable[Composition] table for ancom computation
#       --m-metadata-file Metadata
#       --m-metadata-column MetadataColumn[Categorical]
# categorical metadata column to test for differential abundance
#       --p-transform-function Choices('sqrt', 'log', 'clr')
# the method to transform feature values before generating volcano plots
#       --p-difference-function Choices('mean_difference', 'f_statistic')
# method applied to visualize fold difference in feature abundance
#       --p-filter-missing/no-filter-missing
# if true samples with missing metadata values will be filtered otherwise error


def plot_scatterplot(output_dir: str, metadata: Metadata, title: str,
                     x_label: str, y_label: str):
    J_ENV = jinja2.Environment(
        loader=jinja2.PackageLoader('q2_vizard', 'assets/scatterplot')
    )

    index = J_ENV.get_template('index.html')
    df = metadata.to_dataframe()
    data = json.loads(df.to_json(orient='records'))

    spec_fp = pkg_resources.resource_filename(
        'q2_vizard', os.path.join('assets', 'scatterplot', 'spec.json')
    )
    with open(spec_fp) as fh:
        json_obj = json.load(fh)

    full_spec = json_replace(
        json_obj, data=data, x_label=x_label, y_label=y_label, title=title
    )

    with open(os.path.join(output_dir, "index.html"), "w") as fh:
        spec_string = json.dumps(full_spec)
        fh.write(index.render(spec=spec_string))
