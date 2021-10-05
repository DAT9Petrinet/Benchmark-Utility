import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names):
    sns.set_theme(style="whitegrid", palette="pastel")

    # data from each csv will become a row in the combined dataframe, such that row index is the test name,
    # and columns are answered, not answered, not simplified, simplified and reduced.
    # Some columns are then removed for plotting
    combined = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Change 'NONE' value to 'not answered', and 'TRUE' and 'FALSE' to 'answered'
        data.loc[data.answer != "NONE", "answer"] = "answered"
        data.loc[data.answer == "NONE", "answer"] = "not answered"

        # Same thing for simplification, renames to simplified and not simplified, based on bool value
        data.loc[data['solved by query simplification'], 'solved by query simplification'] = "simplified"
        data.loc[data['solved by query simplification'] == False, 'solved by query simplification'] = "not simplified"

        # Get counts of 'answered' and 'not answered'
        answers = (data['answer'].value_counts()).to_frame()
        # Get counts of 'simplified' and 'not simplified'
        simplifications = (data['solved by query simplification'].value_counts()).to_frame()
        # Combine into same dataframe, with column being the test name, and row indices being above metrics
        answers.rename(columns={'answer': test_names[index]}, inplace=True)
        simplifications.rename(columns={'solved by query simplification': test_names[index]}, inplace=True)
        temp = answers.append(simplifications)

        # Create new column 'reduced'
        temp.loc['reduced'] = temp.T['answered'] - temp.T['simplified']
        temp = temp.T

        # Remove the columns that Nicolaj doesn't like
        temp.drop(columns=['answered', 'not simplified'], inplace=True)

        # Reorder the columns so that bars are stacked nicely
        order = [2, 1, 0]
        temp = temp[[temp.columns[i] for i in order]]

        # Add these result, to results from other csv's
        combined = combined.append(temp)

    # Make stacked bar plot
    plot = combined.plot(kind='bar', stacked=True)
    # For some reason seaborn really wants to rotate the labels, so i un-rotate them
    for item in plot.get_xticklabels():
        item.set_rotation(0)
    plt.legend(loc='upper right')
    plt.ylabel("test instances")
    plt.savefig('../graphs/answer_simplification_bars.png')
    plt.clf()
