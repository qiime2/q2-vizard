# q2-vizard

![](https://github.com/qiime2/q2-vizard/workflows/ci-dev/badge.svg)

The first choice of wizard lizards for interactive, generalized microbiome data visualization!
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/vizarded-lizard-wizard.png)

**Please note that q2-vizard is currently in an alpha release state.** While this plugin can be installed as a conda package, _it has not been tested in integration against our other plugins yet and its API is still subject to change_. It is slated to be officially released in 2024.10 within the QIIME 2 Amplicon and Metagenome distributions. In the meantime, please follow install instructions below if you'd like to take it for a test drive!

## Installing q2-vizard (pre-2024.10 Release)

1. Install conda using the same instructions provided in the [QIIME 2 User Docs](https://docs.qiime2.org/2024.5/install/native/#miniconda).

2. Create a `q2-vizard development environment` using the 2024.5 environment file included in this repository:
```
conda env create -n q2dev-vizard -f https://raw.githubusercontent.com/qiime2/q2-vizard/dev/environment-files/2024.5-vizard-environment.yml
```
2. Activate your new environment and enjoy!
```
conda activate q2dev-vizard
```

## Using q2-vizard (pre-2024.10 Release)

The following Metadata vizualizations are available for use, with examples below!

## scatterplot_2d

This visualizer provides an exploratory view of your Metadata - allowing for any two NumericMetadataColumns to be plotted against each other, with an optional third CategoricalMetadataColumn used for color-coding. You can easily toggle between different measures using the drop downs for X, Y, and colorBy.

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/scatterplot_2d_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/l76or6ts0bz3ueztelttd/viz.qzv?rlkey=v37s02cdzp5dp56n46p3rtdch)


## heatmap

This visualizer generates a heatmap displaying relationships between three Metadata measures. Two of the measures (which can be either categorical or numeric) are mapped to the x and y axes. The third measure (which must be numeric) defines the color gradient of the heatmap, illustrating the intensity or distribution of values across the grid.

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/heatmap_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/q6yrsg1pens7fhzlv14bv/demo-heatmap.qzv?rlkey=eoomz6gw8vcku7kbfjbqurulw)


## lineplot

Coming soon!


## boxplot

Coming soon!
