import copy

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def plot(data_list, test_names, graph_dir, category):
    """
    Creates a stacked bar for each csv data in data_list,
    where the bars are 'reduced', 'simplified', and 'not answered'
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # data from each csv will become a row in the combined dataframe, such that row index is the test name,
    # and columns are 'not answered', 'simplified', and 'reduced'.
    combined = pd.DataFrame()

    for index, data in enumerate(data_list):
        # Change 'NONE' value to 'not answered', and 'TRUE' and 'FALSE' to 'answered'
        data['answer'] = data['answer'].replace(['TRUE', 'FALSE'], 'answered')
        data['answer'] = data['answer'].replace(['NONE'], 'not answered')

        # Same thing for simplification, renames to simplified and not simplified, based on bool value
        data['solved by query simplification'] = data['solved by query simplification'].replace(True, 'simplified')
        data['solved by query simplification'] = data['solved by query simplification'].replace(False, 'not simplified')

        # Get counts of 'answered' and 'not answered'
        answers = (data['answer'].value_counts()).to_frame()

        # Get counts of 'simplified' and 'not simplified'
        simplifications = (data['solved by query simplification'].value_counts()).to_frame()

        try:
            simplifications.drop('ERR', inplace=True)
        except KeyError:
            pass

        # Combine into same dataframe, with column being the test name, and row indices being above metrics
        answers.rename(columns={'answer': test_names[index]}, inplace=True)
        simplifications.rename(columns={'solved by query simplification': test_names[index]}, inplace=True)

        temp = answers.append(simplifications)

        # Might not have these columns, due to faulty test, so wrap in try-except
        try:
            num_answered = temp.T['answered']
        except:
            num_answered = 0

        try:
            num_simplified = temp.T['simplified']
        except:
            num_simplified = 0

        # Create new column 'reduced'
        reduced = int(num_answered - num_simplified)
        if reduced > 0:
            temp.loc['reduced'] = reduced
        temp = temp.T

        # As per default we want to remove these two columns that Nicolaj does not like
        # But as we saw, we can have faulty experiments where some of these wont exist
        # And if we try to remove something that does not exist, everything stops working
        columns_to_remove = ['answered', 'not simplified', 'ERR']
        for col in columns_to_remove:
            try:
                temp.drop(columns=col, inplace=True)
            except KeyError:
                continue

        # Reorder the columns so that bars are stacked nicely
        try:
            temp = temp[["reduced", "simplified", "not answered", "ERR"]]
        except KeyError:
            temp = temp[["reduced", "simplified", "not answered"]]


        # Add data from this experiment, to results from other experiments
        combined = combined.append(temp)

    # Plot the plot
    combined.rename(utility.rename_test_name_for_paper_presentation(test_names), axis='rows', inplace=True)
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = combined.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10), stacked=True)

    plt.legend(bbox_to_anchor=(0.35, 1.12), loc='upper left', borderaxespad=0)
    plt.xlabel("test instances")
    plt.ylabel('experiments')

    # Find max width, in order to move the very small numbers away from the bars
    max_width = 0
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        max_width = max(width, max_width)
    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                      ha='center', va='center', rotation=45)
    plt.savefig(graph_dir + f'{category}_answer_simplification_bars.svg', dpi=600, format="svg")
    plt.close()
