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

combined = pd.DataFrame()
for index, data in enumerate(data_list):
    test_name = test_names[index]
    data.loc[data.answer != "NONE", "answer"] = "answered"
    data.loc[data.answer == "NONE", "answer"] = "not answered"
    data.loc[data['solved by query simplification'], 'solved by query simplification'] = "simplified"
    data.loc[data['solved by query simplification'] == False, 'solved by query simplification'] = "not simplified"

    answers = (data['answer'].value_counts()).to_frame()
    simplifications = (data['solved by query simplification'].value_counts()).to_frame()
    simplifications.rename(columns={'solved by query simplification': "answer"}, inplace=True)

    temp = answers.append(simplifications)
    temp = temp.divide(2, axis='columns')
    temp.rename(columns={'answer': test_name}, inplace=True)
    combined = combined.append(temp.T)

plot = combined.plot(kind='bar', stacked=True)
for item in plot.get_xticklabels():
    item.set_rotation(0)
plt.legend(loc='upper left')
plt.ylabel("test instances")

plt.savefig(f'graphs/answers_simplification.png')
plt.clf()
