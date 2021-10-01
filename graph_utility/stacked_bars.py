import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]
num_rows = len(data_list[0].index)

for index, data in enumerate(data_list):
    data.loc[data.answer != "None", "answer"] = "answered"
    data.loc[data.answer == "None", "answer"] = "not-answered"

    sns.countplot(data=data, x="answer", color='red').set(xlabel='')
    sns.countplot(data=data, x='solved by query simplification', color='blue').set(xlabel='')

    plt.savefig(f'graphs/stacked_bars_{test_names[index]}.png')
    plt.clf()
