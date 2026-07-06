# q2-vizard

![](https://github.com/qiime2/q2-vizard/workflows/ci-dev/badge.svg)

The first choice of wizard lizards for interactive, generalized microbiome data visualization!
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/vizarded-lizard-wizard.png)

## Installing q2-vizard

`q2-vizard` is included in the [QIIME 2 Amplicon Distribution](https://docs.qiime2.org/2024.10/install/native/#qiime-2-amplicon-distribution) as of 2024.10!
If you'd like to install it separately (within a QIIME 2 Tiny Distribution), please follow the instructions below.

1. Start by installing conda using the same instructions provided in the [QIIME 2 User Docs](https://docs.qiime2.org/2024.5/install/native/#miniconda).

2. Contained in this plugin is an environment file for easy installation within the QIIME 2 Tiny Distribution. You can use the following command to create this environment:
```
conda env create -n q2vizard-2024.10 -f https://raw.githubusercontent.com/qiime2/q2-vizard/dev/environment-files/2024.10-vizard-environment.yml
```
2. Activate your new environment and enjoy!
```
conda activate q2vizard-2024.10
```

## Using q2-vizard

The following Metadata vizualizations are available for use, with examples below!

## scatterplot_2d

This visualizer provides an exploratory view of your Metadata - allowing for any two numeric measures to be plotted against each other, with an optional third categorical measure used for color-coding. You can easily toggle between different measures using the drop downs for X, Y, and colorBy.

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/scatterplot_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/566wegb3fvc10mtms93nk/scatterplot-demo.qzv?rlkey=aay1pjsbketne6sbei8x2luoe)


## lineplot

This visualizer generates a lineplot displaying relationships between two numeric Metadata measures, with an optional third categorical measure for grouping your data into separate lines. If replicates are present within your first numeric measure (plotted on the X-axis), you can select either 'median' or 'mean' for replicate handling, which will create line(s) with the average at each point where replicates are present. All numeric columns present within your Metadata will be available as drop-down options on the Y-axis, but the chosen measure for the X-axis will remain fixed.

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/lineplot_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/r044001aj22qr8b2jrmy7/lineplot-demo.qzv?rlkey=k9nfifazsorn9p51fcy7zsjk8)


## heatmap

This visualizer generates a heatmap displaying relationships between three Metadata measures. Two of the measures (which can be either categorical or numeric) are mapped to the x and y axes. The third measure (which must be numeric) defines the color gradient of the heatmap, illustrating the intensity or distribution of values across the grid.

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/heatmap_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/q6yrsg1pens7fhzlv14bv/heatmap-demo.qzv?rlkey=eoomz6gw8vcku7kbfjbqurulw)


## boxplot

This visualizer generates boxplot(s) displaying relationships between a numerical Metadata measure and a categorical Metadata measure. Users can choose from three whisker calculation methods: percentile-based (9th/91st), min-max, and Tukey's Interquartile Range (IQR).

### Demo
![](https://raw.githubusercontent.com/qiime2/q2-vizard/dev/_assets/boxplot_example.png)

[**Interactive Link**](https://view.qiime2.org/visualization/?src=https://www.dropbox.com/scl/fi/ua9m4ayplk19n1pndanpe/boxplot-demo.qzv?rlkey=7rtzze6jl4ryndi6ukullpg2k)
