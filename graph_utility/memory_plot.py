import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]

for index, data in enumerate(data_list):
    data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
    sns.lineplot(data=data['memory']).set(title=f'{test_names[index]}-memory', ylabel='memory usage',
                                          xlabel='test instances', xticks=list(range(0, len(data.index))), yscale="log")
    plt.savefig(f'graphs/memory_{test_names[index]}.png')
    plt.clf()
