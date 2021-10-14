import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
    """
        Just find how much each experiment has reduced the models
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

    sums = []
    for test_index, data in enumerate(data_list):
        sum = 0
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            reduced_size = row['post place count'] + row['post transition count']
            sum += (pre_size - reduced_size)
        sums.append(sum)

    points_df = pd.DataFrame({'names': test_names, 'sums': sums})

    sns.set_theme(style="darkgrid", palette="pastel")
    plot = sns.barplot(x='sums', y='names', data=points_df)
    plt.xlabel("Total reductions")
    plt.ylabel('Experiments')
    plt.title(f'How much the experiment reduced sizes in total')
    plt.xscale('linear')
    plt.tight_layout()

    # This for-loop puts the number of times each rule has been used, on top of the bar
    for p in plot.patches:
        width = p.get_width()  # get bar length
        plot.text(width/2,  # set the text at 1 unit right of the bar
                  p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                  int(width),  # set variable to display, 2 decimals
                  ha='left',  # horizontal alignment
                  va='center')  # vertical alignment

    plt.savefig(graph_dir + 'total_reductions.png')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir)
