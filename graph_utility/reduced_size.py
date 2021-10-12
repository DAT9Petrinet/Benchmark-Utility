import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir):
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

        # This block should remove all -1 in the reduced_sizes_list
        pre_filter_size = len(reduced_sizes_list)
        reduced_sizes_list = [size for size in reduced_sizes_list if not np.isnan(size)]
        post_filter_size = len(reduced_sizes_list)

        reduced_sizes[f'{test_names[test_index]}'] = pd.Series(reduced_sizes_list, dtype='float64')
        print(
            f"(reduced_size) Test instances not completed by {test_names[test_index]} that were completed by another experiment: {(pre_filter_size - post_filter_size)}")

    for col in reduced_sizes:
        reduced_sizes[col] = reduced_sizes[col].sort_values(ignore_index=True)
    # plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    sns.lineplot(data=reduced_sizes, linewidth=2).set(xlabel='test instances', ylabel='size in percent',
                                                      yscale="linear",
                                                      title=f'Reduced size in comparison to pre size, sorted non-decreasingly')

    plt.legend(loc='best')
    plt.savefig(graph_dir + 'reduced_size_compared.png')
    plt.clf()
