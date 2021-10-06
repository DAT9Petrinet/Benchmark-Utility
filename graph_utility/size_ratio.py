import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, unneeded_columns):
    # Remove test with no reduction
    for index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(index)
            test_names.pop(index)

    # Delete rows
    rows_to_delete = set
    for data in data_list:
        # Find all indices where the query has been solved by simplification
        simplification_indices = set((data.index[data['solved by query simplification']]).tolist())

        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Take the intersection
        rows_to_delete = rows_to_delete.intersection((answer_indices.union(simplification_indices)))

    # Remove the rows, columns not needed, and group the data based on models
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)
        data.drop(columns=unneeded_columns, inplace=True)

    reduced_sizes = pd.DataFrame()
    for test_index, data in enumerate(data_list):
        reduced_sizes_list = []
        indices = []
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            post_size = row['post place count'] + row['post transition count']
            reduced_size = ((post_size / pre_size) * 100) if post_size > 0 else -1
            reduced_sizes_list.append(reduced_size)
            indices.append(index)

        reduced_sizes_list.sort()
        pre_filter_size = len(reduced_sizes_list)
        reduced_sizes_list = [size for size in reduced_sizes_list if size != -1]
        post_filter_size = len(reduced_sizes_list)
        indices = indices[:-(pre_filter_size - post_filter_size)]
        reduced_sizes[f'{test_names[test_index]}'] = pd.Series(reduced_sizes_list, indices)
        print(
            f"(size-ratio) Test instances not completed by {test_names[test_index]} that were completed by another experiment: {(pre_filter_size - post_filter_size)}")

    # plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    sns.lineplot(data=reduced_sizes).set(xlabel='test instances', ylabel='size in percent', yscale="linear",
                                         title='Reduced size in comparison to pre size, sorted by numerator reduction')
    plt.savefig('../graphs/reduced_size_compared.png')
    plt.clf()
