import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    """
        Gives point for to each experiment, for each (model/query) combination they can reduce to a smaller size
        than another given experiment. Default is (base-rules)
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

    base_results_index = test_names.index(experiment_to_compare_against_name)
    base_results = data_list[base_results_index]
    data_list.pop(base_results_index)
    test_names.pop(base_results_index)

    points = dict()
    sums = []
    for test_index, data in enumerate(data_list):
        sum = 0
        for index, row in data.iterrows():
            base_results_row = base_results.loc[index]

            # Sanity check
            if (base_results_row['model name'] != row['model name']) or (
                    base_results_row['query index'] != row['query index']):
                raise Exception('(reduction_points) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                base_results_reduced_size = (
                        base_results_row['post place count'] + base_results_row['post transition count'])
                reduced_size = row['post place count'] + row['post transition count']
                sum += np.sign(base_results_reduced_size - reduced_size)
            elif (base_results_row['answer'] == 'NONE') and row['answer'] != 'NONE':
                sum += 1
            elif (base_results_row['answer'] != 'NONE') and row['answer'] == 'NONE':
                sum -= 1
            elif (base_results_row['answer'] == 'NONE') and row['answer'] == 'NONE':
                sum += 0
            else:
                raise Exception(
                    '(reduction_points) Should not be able to reach this. '
                    'Something went wrong with the checks for "NONE"')

        sums.append(sum)

    points_df = pd.DataFrame({'names': test_names, 'sums': sums})

    sns.set_theme(style="darkgrid", palette="pastel")
    plot = sns.barplot(x='sums', y='names', data=points_df)
    plt.xlabel("Points")
    plt.ylabel('Experiments')
    plt.title(f'Points given for being better to reduce than ({experiment_to_compare_against_name})')

    # This for-loop puts the number of times each rule has been used, on top of the bar
    for p in plot.patches:
        width = p.get_width()  # get bar length
        plot.text(width + 1,  # set the text at 1 unit right of the bar
                  p.get_y() + p.get_height() / 2,  # get Y coordinate + X coordinate / 2
                  int(width),  # set variable to display, 2 decimals
                  ha='left',  # horizontal alignment
                  va='center')  # vertical alignment

    plt.savefig(graph_dir + 'reduced_points.png')
    plt.clf()


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            ('.csv' in file) and (experiment_to_compare_against_name not in file)]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    try:
        correct_results = pd.read_csv(csv_dir + experiment_to_compare_against_name + '.csv')
    except:
        raise Exception(
            f'(reduction_points)({experiment_to_compare_against_name}) is not present in saved/ and cannot be used as basis for comparison. '
            f'Check if you made a typo in the parameter to the program')

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
