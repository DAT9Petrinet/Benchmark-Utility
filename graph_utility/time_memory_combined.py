import copy
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir):
    """
    Plots both memory and time for each experiment on same graph
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Dataframe to hold data from all csv's
    # Rows will be test-instances
    # Columns are (test_name)-time and (test_name)-memory
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(
            data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Get data from time column sorted
        time_data = ((data['verification time'].sort_values()).reset_index()).drop(columns=
                                                                                   'index')
        # Rename the column to include the name of the test
        time_data.rename(columns={'verification time': f"{test_names[index]}-time"}, inplace=True)

        # Get data from memory column sorted
        memory_data = ((data['verification memory'].sort_values()).reset_index()).drop(columns=
                                                                                       'index')
        # Rename the column to include the name of the test
        memory_data.rename(columns={'verification memory': f"{test_names[index]}-memory"}, inplace=True)

        # Join the time and memory dataframes
        memory_time_data = time_data.join(memory_data)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = memory_time_data
            continue
        combined_df = pd.concat([combined_df, memory_time_data], axis=1)

    # Recolor lines and choose dashes such that all memory-lines gets dashes, and time-lines are not dashes
    # Also make sure the color matches between the two lines for each experiment
    regex = r"(.*)-(time|memory)$"
    sns.set_theme(style="darkgrid")

    def color(t):
        a = np.array([0.5, 0.5, 0.5])
        b = np.array([0.5, 0.5, 0.5])
        c = np.array([1.0, 1.0, 1.0])
        d = np.array([0.0, 0.33, 0.67])

        return a + (b * np.cos(2 * np.pi * (c * t + d)))

    custom_palette = {}
    dashes = []
    for column_index, column in enumerate(combined_df.columns):
        matches = re.finditer(regex, column, re.MULTILINE)
        for match in matches:
            data_type = match.groups()[1]
            if data_type == "time":
                dashes.append((1, 0))
            elif data_type == "memory":
                dashes.append((2, 2))
            else:
                raise Exception("(time_memory_combined) Should not be able to reach this")
            custom_palette[column] = color((column_index + 1) / len(combined_df.columns))

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

    data_to_plot = [combined_df, combined_df_with_with, combined_df_without]
    png_names = ['all', 'with', 'without']
    dashes_list = [dashes, dashes_with, dashes_without]

    # Plot the plot
    for index, data in enumerate(data_to_plot):
        if len(data) == 0 or len(data.columns) == 0:
            continue
        plot = sns.lineplot(data=data, palette=custom_palette,
                            dashes=dashes_list[index])
        plot.set(
            title=f'model checking time and memory per test instance',
            ylabel='seconds or kB',
            xlabel='test instances', yscale="log")
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

        plt.savefig(graph_dir + f'verification_time-memory_per_model_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\time-memory\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
