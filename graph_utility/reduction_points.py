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

    print(f"(reduction_points) Using {experiment_to_compare_against_name} to compare against")

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

    # List to hold the points for each experiment
    total_points = []
    transitions_points = []
    places_points = []
    for test_index, data in enumerate(data_list):
        total_sum = 0
        transition_sum = 0
        place_sum = 0
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
                total_sum += np.sign(base_results_reduced_size - reduced_size)
                transition_sum += np.sign(base_results_row['post transition count'] - row['post transition count'])
                place_sum += np.sign(base_results_row['post place count'] - row['post place count'])
            elif (base_results_row['answer'] == 'NONE') and row['answer'] != 'NONE':
                total_sum += 1
                transition_sum += 1
                place_sum += 1
            elif (base_results_row['answer'] != 'NONE') and row['answer'] == 'NONE':
                total_sum -= 1
                transition_sum -= 1
                place_sum -= 1
            elif (base_results_row['answer'] == 'NONE') and row['answer'] == 'NONE':
                total_sum += 0
                transition_sum += 0
                place_sum += 0
            else:
                raise Exception(
                    '(reduction_points) Should not be able to reach this. '
                    'Something went wrong with the checks for "NONE"')

        total_points.append(total_sum)
        transitions_points.append(transition_sum)
        places_points.append(place_sum)

    points_df = pd.DataFrame(
        {'total': total_points, 'transitions': transitions_points, 'places': places_points})

    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)

    # Plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = points_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

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
        if width < (max_width / 10):
            plot.annotate(int(width), xy=(max_width / 12.5, bottom + height / 2),
                          ha='center', va='center')
        else:
            plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                          ha='center', va='center')

    plt.savefig(graph_dir + 'reduction_points.png', bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) <= 2:
        raise Exception(
            f'(reduction_points) You need to specify more than one csv, the first will be used as basis for comparison')
    else:
        experiment_to_compare_against_path = sys.argv[1]
        experiment_to_compare_against_name = \
            [os.path.split(os.path.splitext(experiment_to_compare_against_path)[0])[1]][0]
        if experiment_to_compare_against_name == 'no-red':
            print('(reduction_points) Cannot use no-red as basis for comparison, as this has no reductions')

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    if len(test_names) == 2:
        if 'no-red' in test_names:
            raise Exception(
                '(reduction_points) if you only compare two experiments, one cannot be no-red, as this is ignored due to comparing the reductions. '
                'Then you end up with no comparisons.')

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
