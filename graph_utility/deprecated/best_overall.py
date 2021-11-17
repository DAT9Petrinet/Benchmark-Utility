import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import utility


def plot(data_list, test_names, graph_dir):
    """
        Gives point for to each experiment, for each (model/query) combination they can reduce to a smaller size
        than another given experiment. Default is (base-rules)
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    if len(test_names) == 2 and 'no-red' in test_names:
        print(
            '(best_overall) beware, probably weird results (in reduction points) in this graph due to comparing only 2 experiments, and one which is no-red')

    # Find test instances that no experiment managed to reduce
    data_list = utility.filter_out_test_instances_that_were_not_reduced_by_any(data_list)

    # Holds results for the 'strictly better' graph
    reduction_points = []
    time_points = []
    memory_points = []
    unique_answers = []
    reduce_times_points = []

    # Holds results for the 'at least as good as runner-up' graph
    reduction_points_eq = []
    time_points_eq = []
    memory_points_eq = []
    reduce_times_points_eq = []

    # Holds the number of answers each experiment get
    answers = []

    for test_index, data in enumerate(data_list):
        # Holds the sum of each experiments points, will be added to above lists
        reduction_sum = 0
        time_sum = 0
        memory_sum = 0
        unique_answers_sum = 0
        reduce_times_sum = 0

        reduction_eq_sum = 0
        time_eq_sum = 0
        memory_eq_sum = 0
        reduce_times_eq_sum = 0

        answers_sum = 0

        # Iterate through each row, and evaluate them one by one
        for index, row in data.iterrows():
            best_time = np.infty
            best_memory = np.infty
            best_reduction = np.infty
            best_reduce_time = np.infty
            anyone_else_answer = False

            # Go through all other experiments
            for test_index2, data2 in enumerate(data_list):

                # Dont compare against itself
                if test_index == test_index2:
                    continue

                # Get row to compare with
                other_row = data2.loc[index]

                # Sanity check
                if (other_row['model name'] != row['model name']) or (
                        other_row['query index'] != row['query index']):
                    raise Exception('(reduction_points) Comparing wrong rows')

                # If the other experiment has no answered, don't use for comparison
                if other_row['answer'] == 'NONE':
                    continue

                # Find the best result among all experiments
                # Dont compare reduction size against no-red, as this always has 0s, would always win trivially
                if test_names[test_index2] != 'no-red':
                    best_reduction = min(best_reduction,
                                         other_row['post place count'] + other_row['post transition count'])
                best_time = min(best_time, other_row['verification time'])
                best_memory = min(best_memory, other_row['verification memory'])
                best_reduce_time = min(best_memory, other_row['reduce time'])
                anyone_else_answer = anyone_else_answer or (other_row['answer'] != 'NONE')

            # Update the sums for the experiment, based on the results of all other experiments
            # But only if we have answered the test instance ourselves (this check could probably be moved before above for-loop)
            if row['answer'] != 'NONE':
                answers_sum += 1
                if row['verification time'] <= best_time:
                    time_eq_sum += 1
                    if row['verification time'] <= 0.9 * best_time:
                        time_sum += 1
                if row['verification memory'] <= best_memory:
                    memory_eq_sum += 1
                    if row['verification memory'] <= 0.9 * best_memory:
                        memory_sum += 1
                if test_names[test_index] != 'no-red':
                    if (row['post place count'] + row['post transition count']) <= best_reduction:
                        reduction_eq_sum += 1
                        if (row['post place count'] + row['post transition count']) <= 0.9 * best_reduction:
                            reduction_sum += 1
                    if row['reduce time'] <= best_reduce_time:
                        reduce_times_eq_sum += 1
                        if row['reduce time'] <= 0.9 * best_reduce_time:
                            reduce_times_sum += 1
                if not anyone_else_answer:
                    unique_answers_sum += 1

        # When we are done with all rows for this experiment, add sums to the lists
        reduction_points.append(reduction_sum)
        time_points.append(time_sum)
        memory_points.append(memory_sum)
        unique_answers.append(unique_answers_sum)
        reduce_times_points.append(reduce_times_sum)
        reduce_times_points_eq.append(reduce_times_eq_sum)
        reduction_points_eq.append(reduction_eq_sum)
        time_points_eq.append(time_eq_sum)
        memory_points_eq.append(memory_eq_sum)
        answers.append(answers_sum)

    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': reduction_points, 'verification memory': memory_points, 'verification time': time_points,
         'unique answers': unique_answers,
         'answered queries': answers, 'reduce time': reduce_times_points})

    points_eq_df = pd.DataFrame(
        {'reduced size': reduction_points_eq, 'verification memory': memory_points_eq,
         'verification time': time_points_eq,
         'answered queries': answers, 'reduce time': reduce_times_points_eq})

    # Rename rows in the dataframe to be names of the experiments
    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)
    points_eq_df.rename(index=new_indices, inplace=True)

    columns_with_with = [test_name for test_name in points_df.T.columns if
                         ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with_with = [test_name for test_name in points_df.T.columns if
                             "with" not in test_name or ("base-rules" in test_name)]
    columns_to_be_removed_by_with = [column for column in points_df.T.columns if column not in columns_with_with]
    columns_to_be_removed_by_without = [column for column in points_df.T.columns if column not in columns_not_with_with]

    points_df_without = points_df.drop(columns_to_be_removed_by_without)
    points_df_with_with = points_df.drop(columns_to_be_removed_by_with)

    points_eq_df_without = points_eq_df.drop(columns_to_be_removed_by_without)
    points_eq_df_with = points_eq_df.drop(columns_to_be_removed_by_with)

    data_to_plot = [points_df, points_df_with_with, points_df_without]
    data_to_plot_eq = [points_eq_df, points_eq_df_with, points_eq_df_without]
    png_names = ['all', 'with', 'without']

    for index, data in enumerate(data_to_plot):
        if len(data) == 0:
            continue
        # Plot the plots
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title('Point given if at least 10% better than runner-up')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(graph_dir + f'10%_better_points_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()

    for index, data in enumerate(data_to_plot_eq):
        if len(data) == 0:
            continue
        # Plot the second plot with with
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title('Point given if at least as good as runner-up')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(graph_dir + f'better_or_eq_points_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\best-experiment\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
