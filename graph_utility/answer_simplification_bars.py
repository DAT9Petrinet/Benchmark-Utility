import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
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

    # The actual test names are replaced by their index in 'test_names',
    # so the mapping from index to test name is printed in console
    print(f"(answer_simplification_bars) map for x-axis:")
    for index, test_name in enumerate(test_names):
        print(f"{index} = {test_name}")

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

        # Combine into same dataframe, with column being the test name, and row indices being above metrics
        answers.rename(columns={'answer': index}, inplace=True)
        simplifications.rename(columns={'solved by query simplification': index}, inplace=True)
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
        columns_to_remove = ['answered', 'not simplified']
        for col in columns_to_remove:
            try:
                temp.drop(columns=col, inplace=True)
            except:
                continue

        # Reorder the columns so that bars are stacked nicely
        # This perfectly fits with the columns should be in exact opposite order :)
        temp = temp[temp.columns[::-1]]

        # Add data from this experiment, to results from other experiments
        combined = combined.append(temp)

    # Make stacked bar plot
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = combined.plot(kind='bar', stacked=True)
    # For some reason seaborn really wants to rotate the labels, so I un-rotate them
    for item in plot.get_xticklabels():
        item.set_rotation(0)
    # Set legend in the top
    plt.legend(bbox_to_anchor=(0.35, 1.12), loc='upper left', borderaxespad=0)

    plt.ylabel("test instances")
    plt.xlabel('experiments')
    # For each patch (basically each rectangle within the bar), add a label.
    for bar in plot.patches:
        plot.text(
            # Put the text in the middle of each bar. get_x returns the start
            # so we add half the width to get to the middle.
            bar.get_x() + bar.get_width() / 2,
            # Vertically, add the height of the bar to the start of the bar,
            # along with the offset.
            bar.get_y() if bar.get_height() < 2500 else (bar.get_height() / 2) + bar.get_y(),
            # This is actual value we'll show.
            round(bar.get_height()) if round(bar.get_height()) > 0 else "",
            # Center the labels and style them a bit.
            ha='center',
            color='black',
            size=10
        )
    plt.savefig(graph_dir + 'answer_simplification_bars.png')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
