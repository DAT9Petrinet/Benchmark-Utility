import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]
data_list = [pd.read_csv(path) for path in paths]

combined = pd.DataFrame()
for index, data in enumerate(data_list):
    data.loc[data.answer != "NONE", "answer"] = "answered"
    data.loc[data.answer == "NONE", "answer"] = "not answered"
    data.loc[data['solved by query simplification'], 'solved by query simplification'] = "simplified"
    data.loc[data['solved by query simplification'] == False, 'solved by query simplification'] = "not simplified"

    answers = (data['answer'].value_counts()).to_frame()
    simplifications = (data['solved by query simplification'].value_counts()).to_frame()
    simplifications.rename(columns={'solved by query simplification': "answer"}, inplace=True)

    temp = answers.append(simplifications)
    temp.rename(columns={'answer': test_names[index]}, inplace=True)
    combined = combined.append(temp.T)

plot = combined.plot(kind='bar', stacked=False)
for item in plot.get_xticklabels():
    item.set_rotation(0)
plt.legend(loc='upper right')
plt.ylabel("test instances")

plt.savefig('graphs/answer_simplification_bars.png')
plt.clf()
