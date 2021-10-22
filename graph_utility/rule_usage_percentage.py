import copy
import os
import re
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir):
    """
    Plots the percentage of models that has used a rule in either of their queries. Creates a plot for each csv
    """
    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Make one plot (png) for each csv
    for index, data in enumerate(data_list):
        # Skip the experiment with no reductions
        if "no-red" in test_names[index]:
            continue

        # Find th erule names
        rules = [column for column in data.columns.tolist() if
                 "rule" in column]

        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group the data by each model, and sum the number of times each rule has been applied by each model
        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')

        # Get the percentage of model that has applied a rule
        percentages = (((((data_grouped_by_model > 0) * 1).mean()) * 100).to_frame()).T

        # Remove the 'Rule' part of e.g 'Rule A'
        percentages.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)

        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.barplot(data=percentages)
        plot.set(title=f'({test_names[index]}) percentage of models using rules', ylabel='uses in \\%', xlabel='rules')
        # Plots numbers above bars
        for p in plot.patches:
            if p.get_height() != 0.0:
                plot.annotate(format(p.get_height(), '.1f'),
                              (p.get_x() + p.get_width() / 2.,
                               p.get_height()),
                              ha='center', va='center',
                              size=12,
                              xytext=(0, 8),
                              textcoords='offset points')
        plt.savefig(graph_dir + f'{test_names[index]}_rule_usage_percentage.png')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\rule-usage\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
