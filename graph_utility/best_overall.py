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

    # Holds results for the 'strictly better' graph
    reduction_points = []
    time_points = []
    memory_points = []
    unique_answers = []

    # Holds results for the 'at least as good as runner-up' graph
    reduction_eq_points = []
    time_eq_points = []
    memory_eq_points = []

    # Holds the number of answers each experiment get
    answers = []
    for test_index, data in enumerate(data_list):
        # Holds the sum of each experiments points, will be added to above lists
        time_sum = 0
        memory_sum = 0
        reduction_sum = 0
        unique_answers_sum = 0
        time_eq_sum = 0
        memory_eq_sum = 0
        reduction_eq_sum = 0
        answers_sum = 0

        # Iterate through each row, and evaluate them one by one
        for index, row in data.iterrows():
            best_time = np.infty
            best_memory = np.infty
            best_reduction = np.infty
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
                if test_names[test_index] != 'no-red':
                    best_reduction = min(best_reduction,
                                         other_row['post place count'] + other_row['post transition count'])
                best_time = min(best_time, other_row['time'])
                best_memory = min(best_memory, other_row['memory'])
                anyone_else_answer = anyone_else_answer or (other_row['answer'] != 'NONE')

            # Update the sums for the experiment, based on the results of all other experiments
            # But only if we have answered the test instance ourselves (this check could probably be moved before above for-loop)
            if row['answer'] != 'NONE':
                answers_sum += 1
                if row['time'] <= best_time:
                    time_eq_sum += 1
                    if row['time'] <= 0.9 * best_time:
                        time_sum += 1
                if row['memory'] <= best_memory:
                    memory_eq_sum += 1
                    if row['memory'] <= 0.9 * best_memory:
                        memory_sum += 1
                if (row['post place count'] + row['post transition count']) <= best_reduction:
                    reduction_eq_sum += 1
                    if (row['post place count'] + row['post transition count']) <= 0.9 * best_reduction:
                        reduction_sum += 1
                if not anyone_else_answer:
                    unique_answers_sum += 1

        # When we are done with all rows for this experiment, add sums to the lists
        reduction_points.append(reduction_sum)
        time_points.append(time_sum)
        memory_points.append(memory_sum)
        unique_answers.append(unique_answers_sum)
        reduction_eq_points.append(reduction_eq_sum)
        time_eq_points.append(time_eq_sum)
        memory_eq_points.append(memory_eq_sum)
        answers.append(answers_sum)

    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduction': reduction_points, 'memory': memory_points, 'time': time_points, 'unique answers': unique_answers,
         'answered queries': answers})

    points_eq_df = pd.DataFrame(
        {'reduction': reduction_eq_points, 'memory': memory_eq_points, 'time': time_eq_points,
         'answered queries': answers})

    # Rename rows in the dataframe to be names of the experiments
    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)
    points_eq_df.rename(index=new_indices, inplace=True)

    columns_with_with = [test_name for test_name in test_names if "with" in test_name]
    columns_not_with_with = [test_name for test_name in test_names if "with" not in test_name]

    points_df_with_with = points_df.drop(columns_not_with_with)
    points_eq_df_with_with = points_eq_df.drop(columns_not_with_with)

    points_df_without_with = points_df.drop(columns_with_with)
    points_eq_df_without_with = points_eq_df.drop(columns_with_with)

    # Plot the plots
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = points_df_with_with.plot(kind='barh', width=0.75, linewidth=2)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.title('Point given if at least 10% better than runner-up')
    plt.xscale('log')
    plt.xlabel("points")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + '10%_better_points_with.png', bbox_inches='tight')
    plt.clf()

    # Plot the second plot with with
    plot = points_eq_df_with_with.plot(kind='barh', width=0.75, linewidth=2)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.title('Point given if at least as good as runner-up')
    plt.xscale('log')
    plt.xlabel("points")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + 'better_or_eq_points_with.png', bbox_inches='tight')
    plt.clf()

    # Plot the plots without with experiments
    plot = points_df_without_with.plot(kind='barh', width=0.75, linewidth=2)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.title('Point given if at least 10% better than runner-up')
    plt.xscale('log')
    plt.xlabel("points")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + '10%_better_points_without.png', bbox_inches='tight')
    plt.clf()

    #
    plot = points_eq_df_without_with.plot(kind='barh', width=0.75, linewidth=2)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
    plt.title('Point given if at least as good as runner-up')
    plt.xscale('log')
    plt.xlabel("points")
    plt.ylabel('experiments')

    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center')

    plt.savefig(graph_dir + 'better_or_eq_points_without.png', bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read data given as arguments
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find name of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir)
