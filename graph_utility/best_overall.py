import copy
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def get_strictly_better_points(derived_jable, metric, test_names, keep_largest_percent, how_much_better):
    derived_jable = utility.largest_x(derived_jable, keep_largest_percent, metric, test_names)

    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]

    def equally_good_as_runner_up(row, test, metric):
        s = utility.second_smallest_in_list(row.values)
        if metric == 'reduce size':
            return row[test + '@' + metric] < (1 + how_much_better) * s
        return row[test + '@' + metric] < (1 - how_much_better) * s

    def point(row):
        if equally_good_as_runner_up(row[metric_columns], test, metric):
            if metric in ['state space size', 'reduce time']:
                if utility.second_smallest_in_list(row[metric_columns].values) != 0:
                    return 1
                else:
                    return 0
            return 1
        else:
            return 0

    df = pd.DataFrame()
    for test in test_names:
        if metric in ['verification time', 'verification memory', 'total time']:
            df[test + '@' + metric] = derived_jable[metric_columns].apply(
                point,
                axis=1)
        df[test + '@' + metric] = derived_jable[metric_columns].apply(
            point,
            axis=1)
    return utility.zero_padding(df.sum(), metric, test_names).tolist()


def get_eq_points(derived_jable, metric, test_names, keep_largest_percent):
    derived_jable = utility.largest_x(derived_jable, keep_largest_percent, metric, test_names)

    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]

    def equally_good_as_runner_up(row, test, metric):
        s = utility.second_smallest_in_list(row.values)
        return row[test + '@' + metric] <= s

    def point(row):
        if equally_good_as_runner_up(row[metric_columns], test, metric):
            if metric in ['state space size', 'reduce time']:
                if utility.second_smallest_in_list(row[metric_columns].values) != 0:
                    return 1
                else:
                    return 0
            return 1
        else:
            return 0

    df = pd.DataFrame()
    for test in test_names:
        if metric in ['verification time', 'verification memory', 'total time']:
            df[test + '@' + metric] = derived_jable[metric_columns].apply(
                point,
                axis=1)
        df[test + '@' + metric] = derived_jable[metric_columns].apply(
            point,
            axis=1)
    return utility.zero_padding(df.sum(), metric, test_names).tolist()


def get_answer_df(derived_jable, test_names):
    s = pd.Series(dtype=float)
    for test_name in test_names:
        s[test_name] = len(derived_jable[test_name + '@' + 'answer']) - (
            derived_jable[test_name + '@' + 'answer'].value_counts()['NONE'])

    return s.tolist()


def plot(data_list, test_names, graph_dir, keep_largest_percent, how_much_better):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    if len(test_names) == 2 and 'no-red' in test_names:
        print(
            '(best_overall) beware, probably weird results (in reduction points) in this graph due to comparing only 2 experiments, and one which is no-red')

    derived_jable = utility.make_derived_jable(data_list, test_names)

    answer_df = get_answer_df(derived_jable, test_names)
    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': get_strictly_better_points(derived_jable, 'reduced size', test_names, keep_largest_percent,
                                                    how_much_better),
         'state space size': get_strictly_better_points(derived_jable, 'state space size', test_names,
                                                        keep_largest_percent, how_much_better),
         'reduce time': get_strictly_better_points(derived_jable, 'reduce time', test_names, keep_largest_percent,
                                                   how_much_better),
         'verification memory': get_strictly_better_points(derived_jable, 'verification memory', test_names,
                                                           keep_largest_percent, how_much_better),
         'verification time': get_strictly_better_points(derived_jable, 'verification time', test_names,
                                                         keep_largest_percent, how_much_better),
         'total time': get_strictly_better_points(derived_jable, 'total time', test_names,
                                                  keep_largest_percent, how_much_better),
         'answered queries': answer_df,
         'unique answers': utility.zero_padding(derived_jable['unique answers'].value_counts(), 'unique answers',
                                                test_names).tolist(),
         }, index=test_names)

    points_eq_df = pd.DataFrame(
        {'reduced size': get_eq_points(derived_jable, 'reduced size', test_names, keep_largest_percent
                                       ),
         'state space size': get_eq_points(derived_jable, 'state space size', test_names, keep_largest_percent
                                           ),
         'reduce time': get_eq_points(derived_jable, 'reduce time', test_names, keep_largest_percent),
         'verification memory': get_eq_points(derived_jable, 'verification memory', test_names, keep_largest_percent
                                              ),
         'verification time': get_eq_points(derived_jable, 'verification time', test_names, keep_largest_percent
                                            ),
         'total time': get_eq_points(derived_jable, 'total time', test_names,
                                     keep_largest_percent),
         'answered queries': answer_df,
         }, index=test_names)

    data_to_plot = utility.split_into_all_with_without(points_df)
    data_to_plot_eq = utility.split_into_all_with_without(points_eq_df)
    png_names = ['all', 'with', 'without']

    for index, data in enumerate(data_to_plot):
        if index > 0:
            continue
        if len(data) == 0:
            continue
        # Plot the plots
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title(
            f'Point given if at least {how_much_better * 100}% better than runner-up, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests)')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(
            graph_dir + f'{how_much_better * 100}%_better_points_{png_names[index]}_largest_{keep_largest_percent * 100}%tests.png',
            bbox_inches='tight')
        plt.clf()

    for index, data in enumerate(data_to_plot_eq):
        if index > 0:
            continue
        if len(data) == 0:
            continue
        # Plot the second plot with with
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title(
            f'Point given if at least as good as runner-up, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests)')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(
            graph_dir + f'better_or_eq_points_{png_names[index]}_largest_{keep_largest_percent * 100}%tests.png',
            bbox_inches='tight')
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
