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
    sns.violinplot(data=data[rules], bw=.1).set(title=f'{test_names[index]}', ylabel='uses')
    plt.savefig(f'graphs/violin_plot_{test_names[index]}.png')
    plt.clf()
