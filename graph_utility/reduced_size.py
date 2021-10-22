import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir):
    """
    Plots how much each experiment has reduced the size (place count + transition count)
    for each model in each test instance (model, query)
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Remove test with no reductions, assume this is named 'no-red'
    # for test_index, name in enumerate(test_names):
    # if 'no-red' in name:
    #   data_list.pop(test_index)
    #  test_names.pop(test_index)

    # Find test instances that no experiment managed to reduce
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

    # Time to actually find the reduced sizes, collect in reduced_sizes
    reduced_sizes = pd.DataFrame()
    for test_index, data in enumerate(data_list):
        # Collect results from each row in this list, used to construct dataframe later
        reduced_sizes_list = []
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            post_size = row['post place count'] + row['post transition count']

            # The check for post_size > 0 is to make sure we actually reduced this test instance
            reduced_size = ((post_size / pre_size) * 100) if post_size > 0 else np.nan
            reduced_sizes_list.append(reduced_size)

        # This block removes all np.nan in the reduced_sizes_list
        # And also all rows that were not reduced (i.e size == 100)
        reduced_sizes_list = [size for size in reduced_sizes_list if (np.isfinite(size) and size < 100)]
        reduced_sizes_list.sort()
        reduced_frame = pd.DataFrame(reduced_sizes_list, columns=[f'{test_names[test_index]}'])

        # Add to the dataframe containing results from all experiments
        reduced_sizes = pd.concat([reduced_sizes, reduced_frame], axis=1)

    def color(t):
        a = np.array([0.5, 0.5, 0.5])
        b = np.array([0.5, 0.5, 0.5])
        c = np.array([1.0, 1.0, 1.0])
        d = np.array([0.0, 0.33, 0.67])

        return a + (b * np.cos(2 * np.pi * (c * t + d)))

    custom_palette = {}
    for column_index, column in enumerate(reduced_sizes.columns):
        custom_palette[column] = color((column_index + 1) / len(reduced_sizes.columns))

    # Add the spacing between markers in plot
    marker_interval = int(len(reduced_sizes.index) / 20)

    columns_with_with = [test_name for test_name in reduced_sizes.columns if
                         ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with_with = [test_name for test_name in reduced_sizes.columns if
                             "with" not in test_name or ("base-rules" in test_name)]
    columns_to_be_removed_by_with = [column for column in reduced_sizes.columns if column not in columns_with_with]
    columns_to_be_removed_by_without = [column for column in reduced_sizes.columns if
                                        column not in columns_not_with_with]

    reduced_sizes_without = reduced_sizes.drop(columns_to_be_removed_by_without, axis=1)
    reduced_sizes_with_with = reduced_sizes.drop(columns_to_be_removed_by_with, axis=1)

    data_to_plot = [reduced_sizes, reduced_sizes_with_with, reduced_sizes_without]
    png_names = ['all', 'with', 'without']

    sns.set_theme(style="darkgrid", palette="pastel")

    for index, data in enumerate(data_to_plot):
        if len(data) == 0:
            continue
        plot = sns.lineplot(data=data, markers=True, dashes=False, markevery=marker_interval,
                            palette=custom_palette)
        plot.set(
            xlabel='test instances',
            ylabel='size in percent',
            yscale="linear",
            title=f'Reduced size in comparison to pre size, sorted non-decreasingly')

        plt.legend(loc='best')
        plt.savefig(graph_dir + f'reduced_size_{png_names[index]}.png')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\reductions\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
