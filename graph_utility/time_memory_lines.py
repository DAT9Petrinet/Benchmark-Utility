import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir, metric):
    """
    Can be called with a column name, and will plot all values from this column sorted as a line.
    Can be called with multiple csvs, and will plot all lines on same graph
    """

    cutoff = 0.9
    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Dataframe to hold data from all csvs
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):

        # Remove rows where query simplification has been used, or where there isn't an answer
        if metric in ['verification time', 'verification memory']:
            data = data.drop(
                data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Get data from relevant column sorted
        metric_data = ((data[f'{metric}'].sort_values()).reset_index()).drop(columns=
                                                                             'index')

        metric_data = metric_data.drop(index=metric_data.index[:int(len(metric_data) * cutoff)],
                                       axis=0)

        # Rename the column to include the name of the test
        metric_data.rename(columns={f'{metric}': f"{test_names[index]}-{metric}"}, inplace=True)

        print(metric_data)

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
    dashes = []
    for column_index, column in enumerate(combined_df.columns):
        if metric == "verification time" or metric == "state space size":
            dashes.append((1, 0))
        elif metric == "verification memory":
            dashes.append((2, 2))
        else:
            raise Exception("(time_memory) Should not be able to reach this")
        custom_palette[column] = color((column_index + 1) / len(combined_df.columns))

    if metric == "verification time":
        unit = 'seconds'
    elif metric == 'verification memory':
        unit = 'kB'
    elif metric == 'state space size':
        unit = 'number of states'

    columns_with_with = [test_name for test_name in combined_df.columns if
                         ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with_with = [test_name for test_name in combined_df.columns if
                             "with" not in test_name or ("base-rules" in test_name)]
    columns_to_be_removed_by_with = [column for column in combined_df.columns if column not in columns_with_with]
    columns_to_be_removed_by_without = [column for column in combined_df.columns if column not in columns_not_with_with]

    dashes_without = [dash for index, dash in enumerate(dashes) if combined_df.columns[index] in columns_not_with_with]
    combined_df_without = combined_df.drop(columns_to_be_removed_by_without, axis=1)

    dashes_with = [dash for index, dash in enumerate(dashes) if combined_df.columns[index] in columns_with_with]
    combined_df_with_with = combined_df.drop(columns_to_be_removed_by_with, axis=1)

    data_to_plot = [(combined_df, dashes), (combined_df_with_with, dashes_with), (combined_df_without, dashes_without)]
    png_names = ['all', 'with', 'without']

    for index, data in enumerate(data_to_plot):
        if len(data[0]) == 0 or len(data[0].columns) == 0:
            continue
        # Plot the plot
        plot = sns.lineplot(data=data[0], palette=custom_palette,
                            dashes=data[1])
        plot.set(
            title=f'model checking {metric} per test instance',
            ylabel=f'{unit}',
            xlabel='test instances', yscale="log")
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

        plt.savefig(graph_dir + f'{metric}_lines_per_model_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\time-memory-size\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    # This plot also takes as argument which column to be used, so here we call with both 'time' and 'memory'
    metrics = ['verification time', 'verification memory', 'state space size']
    for metric in metrics:
        plot(data_list, test_names, graph_dir, metric)
