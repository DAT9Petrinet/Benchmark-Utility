import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)
    # Remove test with no reduction
    for test_index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(test_index)
            test_names.pop(test_index)

    # Delete rows
    rows_to_delete = set
    for data in data_list:
        # Find all indices where the query has been solved by simplification
        simplification_indices = set((data.index[data['solved by query simplification']]).tolist())

        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Take the intersection
        rows_to_delete = rows_to_delete.intersection((answer_indices.union(simplification_indices)))

    # Remove the rows from all data files
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    reduced_sizes = pd.DataFrame()
    for test_index, data in enumerate(data_list):
        reduced_sizes_list = []
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            post_size = row['post place count'] + row['post transition count']
            # The check for post_size > 0 is to make sure we actually got a result,
            # could be NONE in answer, in which case size would be 0, but we are only interested in the ones we could reduce
            reduced_size = ((post_size / pre_size) * 100) if post_size > 0 else np.nan
            reduced_sizes_list.append(reduced_size)

        # This block should remove all np.nan in the reduced_sizes_list
        reduced_sizes_list = [size for size in reduced_sizes_list if (np.isfinite(size) and size < 100)]
        reduced_sizes_list.sort()
        reduced_frame = pd.DataFrame(reduced_sizes_list, columns=[f'{test_names[test_index]}'])
        reduced_sizes = pd.concat([reduced_sizes, reduced_frame], axis=1)

    marker_interval = int(len(reduced_sizes.index) / 20)
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = sns.lineplot(data=reduced_sizes, markers=True, dashes=False, markevery=marker_interval)
    plot.set(
        xlabel='test instances',
        ylabel='size in percent',
        yscale="linear",
        title=f'Reduced size in comparison to pre size, sorted non-decreasingly')

    plt.legend(loc='best')
    plt.savefig(graph_dir + 'reduced_size_compared.png')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    data_list = [pd.read_csv(path) for path in paths]
    plot(data_list, test_names, graph_dir)
