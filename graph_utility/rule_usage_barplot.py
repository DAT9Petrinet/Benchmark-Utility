import matplotlib.pyplot as plt
import numpy
import numpy as np
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

    #percentages = [(len(grouped_data[grouped_data[rule] > 0])) / num_models
    #               for rule in rules]

    percentages = ((grouped_data > 0)*1).mean()
    percentages = (percentages.to_frame()).transpose()
    print(percentages)

    sns.barplot(data=percentages).set(title=f'{test_names[index]}', ylabel='uses in \%')
    plt.savefig(f'graphs/rule_usage_barplot_{test_names[index]}.png')
    plt.clf()
