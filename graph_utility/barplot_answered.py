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
    data.loc[data.answer != "NONE", "answer"] = "answered"
    data.loc[data.answer == "NONE", "answer"] = "not-answered"

    fig, ax = plt.subplots(1, 2)
    plt.subplots_adjust(left=0.125, right=0.9, bottom=0.1, top=0.9, wspace=0.3, hspace=0.2)
    sns.countplot(x=data['answer'], ax=ax[0])
    data_with_answers = data.drop(data[(data.answer == 'not-answered')].index)
    sns.countplot(x=data_with_answers['solved by query simplification'], ax=ax[1]).set(ylabel='')
    plt.savefig(f'graphs/answered_queries_{test_names[index]}.png')
    plt.clf()
