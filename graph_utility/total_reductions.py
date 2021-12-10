import copy
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names, graph_dir):
    """
        Plots 3 bars for each experiment, one for how many transitions, places and both has been reduced
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Remove test with no reductions, assume this is named 'no-red'
    for test_index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(test_index)
            test_names.pop(test_index)

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

    # List to hold the reductions for each experiment
    total_reductions = []
    transitions_reductions = []
    places_reductions = []
    # Go through each experiment
    for test_index, data in enumerate(data_list):
        total_reduction_sum = 0
        transition_reduction_sum = 0
        place_reduction_sum = 0

        # Calculate the reductions, and add to sums
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            reduced_size = row['post place count'] + row['post transition count']
            total_reduction_sum += (pre_size - reduced_size)
            transition_reduction_sum += row['prev transition count'] - row['post transition count']
            place_reduction_sum += row['prev place count'] - row['post place count']

        total_reductions.append(total_reduction_sum)
        transitions_reductions.append(transition_reduction_sum)
        places_reductions.append(place_reduction_sum)

    # Create dataframe
    points_df = pd.DataFrame(
        {'total': total_reductions, 'places': places_reductions, 'transitions': transitions_reductions})

    # Rename indices to be test names, instead of int index
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
        if len(data) == 0 or len(data.columns) == 0:
            continue
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.xscale('log')
        plt.xlabel("reductions")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2),
                          ha='center', va='center')

        plt.savefig(graph_dir + f'total_reductions_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\reductions\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '../results\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir)
