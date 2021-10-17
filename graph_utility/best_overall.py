import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
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

    # List to hold the points for each experiment
    reduction_points = []
    time_points = []
    memory_points = []
    unique_answers = []
    reduction_eq_points = []
    time_eq_points = []
    memory_eq_points = []
    answers = []
    for test_index, data in enumerate(data_list):
        time_sum = 0
        memory_sum = 0
        reduction_sum = 0
        unique_answers_sum = 0
        time_eq_sum = 0
        memory_eq_sum = 0
        reduction_eq_sum = 0
        answers_sum = 0
        for index, row in data.iterrows():
            best_time = np.infty
            best_memory = np.infty
            best_reduction = np.infty
            anyone_else_answer = False
            for test_index2, data2 in enumerate(data_list):
                if test_index == test_index2:
                    continue

                other_row = data2.loc[index]
                if (other_row['model name'] != row['model name']) or (
                        other_row['query index'] != row['query index']):
                    raise Exception('(reduction_points) Comparing wrong rows')

                best_reduction = min(best_reduction, other_row['post place count'] + other_row['post transition count'])
                best_time = min(best_time, other_row['time'])
                best_memory = min(best_memory, other_row['memory'])
                anyone_else_answer = anyone_else_answer or (other_row['answer'] != 'NONE')

            if row['answer'] != 'NONE':
                if row['time'] < best_time:
                    time_sum += 1
                if row['memory'] < best_memory:
                    memory_sum += 1
                if (row['post place count'] + row['post transition count']) < best_reduction:
                    reduction_sum += 1
                if not anyone_else_answer:
                    unique_answers_sum += 1

            if row['answer'] != 'NONE':
                answers_sum += 1
                if row['time'] <= best_time:
                    time_eq_sum += 1
                if row['memory'] <= best_memory:
                    memory_eq_sum += 1
                if (row['post place count'] + row['post transition count']) <= best_reduction:
                    reduction_eq_sum += 1

        reduction_points.append(reduction_sum)
        time_points.append(time_sum)
        memory_points.append(memory_sum)
        unique_answers.append(unique_answers_sum)
        reduction_eq_points.append(reduction_eq_sum)
        time_eq_points.append(time_eq_sum)
        memory_eq_points.append(memory_eq_sum)
        answers.append(answers_sum)

    points_df = pd.DataFrame(
        {'reduction': reduction_points, 'memory': memory_points, 'time': time_points, 'unique answers': unique_answers})

    points_eq_df = pd.DataFrame(
        {'reduction': reduction_eq_points, 'memory': memory_eq_points, 'time': time_eq_points,
         'answers': answers})

    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)
    points_eq_df.rename(index=new_indices, inplace=True)

    # Plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = points_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.xscale('log')
    plt.xlabel("reductions")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + 'best_overall_points.png', bbox_inches='tight')
    plt.clf()

    # Plot the second plot
    # Plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = points_eq_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.xscale('log')
    plt.xlabel("reductions")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + 'best_or_eq_points.png', bbox_inches='tight')
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

    plot(data_list, test_names, graph_dir)
