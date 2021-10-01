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

    num_answered = data['answer'].value_counts()['answered']
    try:
        num_non_answered = data['answer'].value_counts()['not-answered']
    except:
        num_non_answered = 0
    max_y_tick = max(num_answered, num_non_answered)
    sns.countplot(data=data, x="answer").set(title=f'{test_names[index]}-answered-queries', xlabel='',
                                             yticks=list(range(0, max_y_tick + 1)))
    plt.savefig(f'graphs/answered_queries_{test_names[index]}.png')
    plt.clf()
