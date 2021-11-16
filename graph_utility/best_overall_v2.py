import copy
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def zero_padding(series, metric, test_names):
    if metric != 'unique answers':
        metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    else:
        metric_columns = test_names

    for test_name in metric_columns:
        if test_name not in series:
            series[test_name] = 0
    return series


def second_smallest(list):
    return sorted(list)[1]


def get_strictly_better_points(derived_jable, metric, test_names):
    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]

    def find_best(row):
        s = second_smallest(row.values)
        return next(
            iter([experiment for experiment, value in row.items() if value <= 0.9 * s]),
            None)

    df = pd.DataFrame()
    df[metric + ' scores'] = derived_jable[metric_columns].apply(
        find_best,
        axis=1)

    return zero_padding(df.value_counts(), metric, test_names).tolist()


def get_answer_df(derived_jable, test_names):
    s = pd.Series(dtype=float)
    for test_name in test_names:
        s[test_name] = len(derived_jable[test_name + '@' + 'answer']) - (
            derived_jable[test_name + '@' + 'answer'].value_counts()['NONE'])

    return s.tolist()


def plot(data_list, test_names, graph_dir):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    if len(test_names) == 2 and 'no-red' in test_names:
        print(
            '(best_overall) beware, probably weird results (in reduction points) in this graph due to comparing only 2 experiments, and one which is no-red')

    derived_jable = utility.make_derived_jable(data_list, test_names)

    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': get_strictly_better_points(derived_jable, 'reduced size', test_names),
         'state space size': get_strictly_better_points(derived_jable, 'state space size', test_names),
         'reduce time': get_strictly_better_points(derived_jable, 'reduce time', test_names),
         'verification memory': get_strictly_better_points(derived_jable, 'verification memory', test_names),
         'verification time': get_strictly_better_points(derived_jable, 'verification time', test_names),
         'answered queries': get_answer_df(derived_jable, test_names),
         'unique answers': zero_padding(derived_jable['unique answers'].value_counts(), 'unique answers',
                                        test_names).tolist(),
         })

    # points_eq_df = pd.DataFrame(
    #   {'reduced size': reduction_points_eq, 'verification memory': memory_points_eq,
    #    'verification time': time_points_eq,
    #  'answered queries': answers, 'reduce time': reduce_times_points_eq})

    # Rename rows in the dataframe to be names of the experiments
    new_indices = dict()
    for index, name in enumerate(test_names):
        new_indices[index] = name
    points_df.rename(index=new_indices, inplace=True)
    # points_eq_df.rename(index=new_indices, inplace=True)

    columns_with_with = [test_name for test_name in points_df.T.columns if
                         ("with" in test_name) or ("base-rules" in test_name)]
    columns_not_with_with = [test_name for test_name in points_df.T.columns if
                             "with" not in test_name or ("base-rules" in test_name)]

    columns_to_be_removed_by_with = [column for column in points_df.T.columns if column not in columns_with_with]
    columns_to_be_removed_by_without = [column for column in points_df.T.columns if column not in columns_not_with_with]

    points_df_without = points_df.drop(columns_to_be_removed_by_without)
    points_df_with_with = points_df.drop(columns_to_be_removed_by_with)

    # points_eq_df_without = points_eq_df.drop(columns_to_be_removed_by_without)
    # points_eq_df_with = points_eq_df.drop(columns_to_be_removed_by_with)

    data_to_plot = [points_df, points_df_with_with, points_df_without]
    # data_to_plot_eq = [points_eq_df, points_eq_df_with, points_eq_df_without]
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

    '''for index, data in enumerate(data_to_plot_eq):
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
        plt.clf()'''


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
