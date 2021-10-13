import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, graph_dir):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)
    pd.set_option('display.max_rows', None)

    # Remove test with no reduction
    for index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(index)
            test_names.pop(index)

    # Find indices to remove
    # Cannot simply remove them per csv, we have to go through all csvs first, and
    # find any rows that has been solved by simplification, or has 'NONE' answers, as they should be removed from all csv
    # Also find all previous sizes
    rows_to_delete = set
    prev_sizes = pd.DataFrame()
    for data in data_list:
        for index, row in data.iterrows():
            # If we dont know the size, or we already have the size, continue
            if row['prev place count'] == 0 or index in prev_sizes.index:
                continue
            # Else add the previous size
            else:
                prev_size = row['prev place count'] + row['prev transition count']
                new_row = pd.Series(data={'size': prev_size}, name=index)
                prev_sizes = prev_sizes.append(new_row, ignore_index=False)

        # Find all indices where the query has been solved by simplification
        simplification_indices = set((data.index[data['solved by query simplification']]).tolist())

        # Find all rows where we have 'NONE' answer
        answer_indices = set((data.index[data['answer'] == 'NONE']).tolist())

        # Take the intersection
        rows_to_delete = rows_to_delete.intersection((answer_indices.union(simplification_indices)))

    # Remove the rows, columns not needed, and group the data based on models
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    # Get sizes from the data that will be used as numerator
    numerator_sizes = pd.DataFrame()
    for index, row in data_list[0].iterrows():
        post_size = row['post place count'] + row['post transition count']
        pre_size = row['prev place count'] + row['prev transition count']
        reduced_size = ((post_size / pre_size) * 100) if post_size > 0 else 0
        new_row = pd.Series(data={'prev size': pre_size, 'post size': post_size, 'reduced size': reduced_size},
                            name=index)
        numerator_sizes = numerator_sizes.append(new_row, ignore_index=False)

    # Dataframe to hold the size ratio between reduced nets
    size_ratios = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list):
        # Dont compare size against the numerator, would just be 1 and a quite boring line
        if test_index == 0:
            continue

        ratios = pd.DataFrame()

        # Iterate through all rows and compute ratio
        # All this with lists and stuff, and this iteration should probaly be handled better using pandas, but works :shrug
        for index, row in data.iterrows():
            size_pre_reductions = int(row['prev place count'] + row['prev transition count'])

            # Check if this csv has managed to complete the query
            if size_pre_reductions == 0:
                ratios = ratios.append(pd.Series(data={'size': np.infty}, name=index), ignore_index=False)
            elif numerator_sizes.loc[index]['post size'] == 0:
                ratios = ratios.append(pd.Series(data={'size': np.nan}, name=index), ignore_index=False)
            elif size_pre_reductions != 0:
                # Sanity check
                if prev_sizes.loc[index]['size'] != size_pre_reductions:
                    raise Exception("Not comparing same rows")

                post_size = row['post place count'] + row['post transition count']
                ratio = numerator_sizes.loc[index]['post size'] / post_size
                new_row = pd.Series(data={'size': ratio}, name=index)
                ratios = ratios.append(new_row, ignore_index=False)
            else:
                raise Exception("Should not be able to reach this")

        # Add ratios to the current dataframe, with the tests being compared as the column name
        size_ratios[f"{test_names[0]}/{test_names[test_index]}"] = ratios

    size_ratios = (size_ratios.join(numerator_sizes['reduced size'])).sort_values('reduced size')
    size_ratios.reset_index(inplace=True, drop=True)
    size_ratios.drop(columns='reduced size', inplace=True)
    # plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    sns.lineplot(data=size_ratios).set(xlabel='test instance', ylabel='size ratio', yscale="log",
                                       title='Reduced size of nets')
    plt.savefig(graph_dir + 'reduced_size_compared.png')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    data_list = [pd.read_csv(path) for path in paths]
    plot(data_list, test_names, graph_dir)
