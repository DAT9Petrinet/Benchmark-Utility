import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]
rules = [column for column in (pd.read_csv(paths[0], index_col=0, nrows=0).columns.tolist()) if "rule" in column]

for index, data in enumerate(data_list):
    data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
    grouped_data = data.groupby(['model name'])[rules].agg('sum')
    num_models = len(grouped_data)

    percentages = (((((grouped_data > 0) * 1).mean()) * 100).to_frame()).transpose()

    plot = sns.barplot(data=percentages)
    plot.set(title=f'({test_names[index]}) percentage of models using rules', ylabel='uses in \%')
    for p in plot.patches:
        plot.annotate(format(p.get_height(), '.1f'),
                      (p.get_x() + p.get_width() / 2., p.get_height()),
                      ha='center', va='center',
                      size=10,
                      xytext=(0, 8),
                      textcoords='offset points')
    plt.savefig(f'../graphs/{test_names[index]}_rule_usage_percentage.png')
    plt.clf()
