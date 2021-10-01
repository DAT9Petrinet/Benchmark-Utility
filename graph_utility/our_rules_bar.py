import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]
rules = ["rule L"]
for index, data in enumerate(data_list):
    data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
    sns.barplot(data=data[rules]).set(title=f'{test_names[index]}-how often were our rules used', ylabel='uses')
    plt.savefig(f'graphs/our_rules_uses_bar_plot_{test_names[index]}.png')
    plt.clf()
