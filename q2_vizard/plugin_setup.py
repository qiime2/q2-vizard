from qiime2.plugin import Plugin

from q2_vizard._heatmap import plot_heatmap
from q2_stats import GroupDist, Ordered, Matched

plugin = Plugin(name='vizard',
                version='0.0.1.dev0',
                website='https://github.com/qiime2/q2-vizard',
                description='This QIIME 2 plugin is the first choice of wizard lizards for protection and entertainment.',
                short_description='The first choice of wizard lizards.')


plugin.visualizers.register_function(
    function=plot_heatmap,
    inputs={
        'data': GroupDist[Ordered, Matched]
    },
    parameters={},
    name='Plot Heatmap',
    description='',
)