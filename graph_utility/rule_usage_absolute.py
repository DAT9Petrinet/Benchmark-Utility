import os
import re
import sys
import warnings
import copy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("error")


def plot(data_list, test_names, graph_dir):
    """
    Plots the number of times each rule has been used across all test instances. Creates a plot for each csv
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Make one plot (png) for each csv
    for test_index, data in enumerate(data_list):
        # Skip the experiment with no reductions
        if "no-red" in test_names[test_index]:
            continue

        # Find rule names
        rules = [column for column in data.columns.tolist() if
                 "rule" in column]

        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Sum over all rows the number of times each rule has been used
        rules_summed = data[rules].agg('sum').to_frame().T

        # Remove the 'Rule' part of e.g 'Rule A'
        rules_summed.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)

        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.barplot(data=rules_summed)
        try:
            plot.set_yscale("log")
        except:
            print(f"Test has probably gone wrong, had no application of any rules: {test_names[test_index]}")
            plot.set_yscale("linear")
        plot.set(title=f'({test_names[test_index]}) number of times rules are used', ylabel='uses', xlabel='rules')
        # This for-loop puts the number of times each rule has been used, on top of the bar
        for p in plot.patches:
            plot.annotate(format(p.get_height().astype(int), 'd'),
                          ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(graph_dir + f'{test_names[test_index]}_rule_usage_absolute.png')
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
