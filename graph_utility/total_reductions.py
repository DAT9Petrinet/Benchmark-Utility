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

    total = []
    transitions = []
    places = []
    for test_index, data in enumerate(data_list):
        total_reduction_row = 0
        transition_reduction_row = 0
        place_reduction_row = 0
        for index, row in data.iterrows():
            pre_size = row['prev place count'] + row['prev transition count']
            reduced_size = row['post place count'] + row['post transition count']
            total_reduction_row += (pre_size - reduced_size)
            transition_reduction_row += row['prev transition count'] - row['post transition count']
            place_reduction_row += row['prev place count'] - row['post place count']
        total.append(total_reduction_row)
        transitions.append(transition_reduction_row)
        places.append(place_reduction_row)

    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name

    points_df = pd.DataFrame({'total': total, 'places': places, 'transitions': transitions})
    points_df.rename(index=new_indices, inplace=True)
    print(points_df)

    sns.set_theme(style="darkgrid", palette="pastel")
    plot = points_df.plot(kind='barh', stacked=True)

    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

    plt.xlabel("reductions")
    plt.ylabel('experiments')
    # For each patch (basically each rectangle within the bar), add a label.
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                      ha='center', va='center')

    plt.savefig(graph_dir + 'total_reductions.png', bbox_inches='tight')
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
