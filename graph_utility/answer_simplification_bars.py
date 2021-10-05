import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names):
    sns.set_style("whitegrid")
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
        temp.loc['reduced'] = temp.T['answered'] - temp.T['simplified']
        temp = temp.T
        # Remove the columns that Nicolaj doesnt like
        temp.drop(columns=['answered', 'not simplified'], inplace=True)

        # Reorder the columns so that bars are stacked nicely
        order = [2, 1, 0]  # setting column's order
        temp = temp[[temp.columns[i] for i in order]]

        combined = combined.append(temp)

    plot = combined.plot(kind='bar', stacked=True)
    for item in plot.get_xticklabels():
        item.set_rotation(0)
    plt.legend(loc='upper right')
    plt.ylabel("test instances")

    plt.savefig('../graphs/answer_simplification_bars.png')
    plt.clf()
