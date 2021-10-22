import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    """
        Gives point for to each experiment, for each (model/query) combination they can reduce to a smaller size
        than another given experiment. Default is (base-rules)
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    print(f"(time_memory_points) using ({experiment_to_compare_against_name}) to compare against")

    # Find test instances that no experiment managed to find an answer to
    rows_to_delete = set()
    for index, data in enumerate(data_list):
        # Find all indices where the query has been solved by simplification
        simplification_indices = set((data.index[data['solved by query simplification']]).tolist())

        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Take the union
        combined_indices = answer_indices.union(simplification_indices)

        # Only interested in finding the rows that NO experiment managed to reduce
        # So take intersection
        if index == 0:
            rows_to_delete = combined_indices
        else:
            rows_to_delete = rows_to_delete.intersection(combined_indices)

    # Remove the rows from all data files
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    base_results_index = test_names.index(experiment_to_compare_against_name)
    base_results = data_list[base_results_index]
    data_list.pop(base_results_index)
    test_names.pop(base_results_index)

    # List to hold the points for each experiment
    time_points = []
    memory_points = []

    for test_index, data in enumerate(data_list):
        time_sum = 0
        memory_sum = 0

        for index, row in data.iterrows():
            base_results_row = base_results.loc[index]

            # Sanity check
            if (base_results_row['model name'] != row['model name']) or (
                    base_results_row['query index'] != row['query index']):
                raise Exception('(time_memory_points) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                time_sum += np.sign(base_results_row['time'] - row['time'])
                memory_sum += np.sign(base_results_row['memory'] - row['memory'])
            elif (base_results_row['answer'] == 'NONE') and row['answer'] != 'NONE':
                time_sum += 1
                memory_sum += 1
            elif (base_results_row['answer'] != 'NONE') and row['answer'] == 'NONE':
                time_sum -= 1
                memory_sum -= 1
            elif (base_results_row['answer'] == 'NONE') and row['answer'] == 'NONE':
                time_sum += 0
                memory_sum += 0
            else:
                raise Exception(
                    '(time_memory_points) Should not be able to reach this. '
                    'Something went wrong with the checks for "NONE"')

        time_points.append(time_sum)
        memory_points.append(memory_sum)

    points_df = pd.DataFrame(
        {'time': time_points, 'memory': memory_points})

    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)

    columns_with_with = [test_name for test_name in points_df.T.columns if
                         ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with_with = [test_name for test_name in points_df.T.columns if
                             "with" not in test_name or ("base-rules" in test_name)]
    columns_to_be_removed_by_with = [column for column in points_df.T.columns if column not in columns_with_with]
    columns_to_be_removed_by_without = [column for column in points_df.T.columns if column not in columns_not_with_with]

    points_df_without = points_df.drop(columns_to_be_removed_by_without)
    points_df_with_with = points_df.drop(columns_to_be_removed_by_with)

    data_to_plot = [points_df, points_df_with_with, points_df_without]
    png_names = ['all', 'with', 'without']

    for index, data in enumerate(data_to_plot):
        if len(data) == 0:
            continue
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.xscale('linear')
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title(f'Comparing experiments to ({experiment_to_compare_against_name})')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Find max width, in order to move the very small numbers away from the bars
        max_width = 0
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            max_width = max(width, max_width)
        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            left += 1
            plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                          ha='center', va='center')

        plt.savefig(graph_dir + f'time_memory_points_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) <= 2:
        raise Exception(
            f'(time_memory_points) You need to specify more than one csv, the first will be used as basis for comparison')
    else:
        experiment_to_compare_against_name = [os.path.split(os.path.splitext(sys.argv[1])[0])[1]][0]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\time-memory\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
