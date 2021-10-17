import math
import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import copy
import numpy as np


def plot(data_list, test_names, graph_dir, metric):
    """
    Can be called with a column name, and will plot all values from this column sorted as a line.
    Can be called with multiple csvs, and will plot all lines on same graph
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Dataframe to hold data from all csvs
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(
            data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Get data from relevant column sorted
        metric_data = ((data[f'{metric}'].sort_values()).reset_index()).drop(columns=
                                                                             'index')
        # Rename the column to include the name of the test
        metric_data.rename(columns={f'{metric}': f"{index}"}, inplace=True)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = metric_data
            continue
        combined_df = pd.concat([combined_df, metric_data], axis=1)

    # Make sure colors and dashes matches the ones from 'time_memory_combined'
    def color(t):
        a = np.array([0.5, 0.5, 0.5])
        b = np.array([0.5, 0.5, 0.5])
        c = np.array([1.0, 1.0, 1.0])
        d = np.array([0.0, 0.33, 0.67])

        return a + (b * np.cos(2 * np.pi * (c * t + d)))

    sns.set_theme(style="darkgrid")
    custom_palette = {}
    for column_index, column in enumerate(combined_df.columns):
        custom_palette[column] = color((column_index + 1) / len(combined_df.columns))

    if metric == 'time':
        unit = 'seconds'
    else:
        unit = 'kB'

    # Plot the plot
    plot = sns.boxenplot(data=combined_df, palette=custom_palette)
    plot.set(
        title=f'model checking {metric} per experiment',
        ylabel=f'{unit}',
        xlabel='test instances', yscale="log")

    plt.savefig(graph_dir + f'{metric}_box_per_model.png', bbox_inches='tight')
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

    # This plot also takes as argument which column to be used, so here we call with both 'time' and 'memory'
    metrics = ['time', 'memory']
    for metric in metrics:
        plot(data_list, test_names, graph_dir, metric)
