import copy
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility

keep_largest_percent = 0.1
how_much_better = 0.1


def zero_padding(series, metric, test_names):
    if metric != 'unique answers':
        metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    else:
        metric_columns = test_names

    for test_name in metric_columns:
        if test_name not in series or (test_name == 'no-red' and metric in ['reduce time', 'reduced size']):
            series[test_name] = 0
    return series


def second_smallest(list):
    return sorted(list)[1]


def second_largest(list):
    return sorted(list)[-2]


def get_strictly_better_points(derived_jable, metric, test_names, experiment_to_compare_against):
    derived_jable = utility.largest_x(derived_jable, keep_largest_percent, metric, test_names)

    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]

    def better_than_comparison(row, test, metric):
        if metric == 'reduced size':
            return row[test + '@' + metric] > row[experiment_to_compare_against + '@' + metric]
        else:
            return row[test + '@' + metric] < row[experiment_to_compare_against + '@' + metric]

    def point(row):
        if better_than_comparison(row[metric_columns], test, metric):
            if metric in ['verification time', 'verification memory', 'reduce time']:
                return 1
            elif metric in ['state space size']:
                if second_smallest(row[metric_columns].values) != 0:
                    return 1
                else:
                    return 0
            elif metric in ['reduced size']:
                return 1
        else:
            return 0

    df = pd.DataFrame()
    for test in test_names:
        df[test + '@' + metric] = derived_jable[metric_columns].apply(
            point,
            axis=1)

    return zero_padding(df.sum(), metric, test_names).tolist()


def get_eq_points(derived_jable, metric, test_names, experiment_to_compare_against):
    derived_jable = utility.largest_x(derived_jable, keep_largest_percent, metric, test_names)

    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]

    def better_than_comparison(row, test, metric):
        if metric == 'reduced size':
            return row[test + '@' + metric] >= row[experiment_to_compare_against + '@' + metric]
        else:
            return row[test + '@' + metric] <= row[experiment_to_compare_against + '@' + metric]

    def point(row):
        if better_than_comparison(row[metric_columns], test, metric):
            if metric in ['verification time', 'verification memory', 'reduce time']:
                return 1
            elif metric in ['state space size']:
                if second_smallest(row[metric_columns].values) != 0:
                    return 1
                else:
                    return 0
            elif metric in ['reduced size']:
                return 1
        else:
            return 0

    df = pd.DataFrame()
    for test in test_names:
        df[test + '@' + metric] = derived_jable[metric_columns].apply(
            point,
            axis=1)

    return zero_padding(df.sum(), metric, test_names).tolist()


def get_answer_df(derived_jable, test_names):
    s = pd.Series(dtype=float)
    for test_name in test_names:
        s[test_name] = len(derived_jable[test_name + '@' + 'answer']) - (
            derived_jable[test_name + '@' + 'answer'].value_counts()['NONE'])

    return s.tolist()


def plot(data_list, test_names, graph_dir, experiment_to_compare_against):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    if len(test_names) == 2 and 'no-red' in test_names:
        print(
            '(best_overall) beware, probably weird results (in reduction points) in this graph due to comparing only 2 experiments, and one which is no-red')

    derived_jable = utility.make_derived_jable(data_list, test_names)

    answer_df = get_answer_df(derived_jable, test_names)
    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': get_strictly_better_points(derived_jable, 'reduced size', test_names,
                                                    experiment_to_compare_against),
         'state space size': get_strictly_better_points(derived_jable, 'state space size', test_names,
                                                        experiment_to_compare_against),
         'reduce time': get_strictly_better_points(derived_jable, 'reduce time', test_names,
                                                   experiment_to_compare_against),
         'verification memory': get_strictly_better_points(derived_jable, 'verification memory', test_names,
                                                           experiment_to_compare_against),
         'verification time': get_strictly_better_points(derived_jable, 'verification time', test_names,
                                                         experiment_to_compare_against),
         'answered queries': answer_df,
         'unique answers': zero_padding(utility.unique_answers_comparison(derived_jable, experiment_to_compare_against, test_names), 'unique answers',
                                        test_names).tolist(),
         }, index=test_names)

    points_eq_df = pd.DataFrame(
        {'reduced size': get_eq_points(derived_jable, 'reduced size', test_names, experiment_to_compare_against),
         'state space size': get_eq_points(derived_jable, 'state space size', test_names,
                                           experiment_to_compare_against),
         'reduce time': get_eq_points(derived_jable, 'reduce time', test_names, experiment_to_compare_against),
         'verification memory': get_eq_points(derived_jable, 'verification memory', test_names,
                                              experiment_to_compare_against),
         'verification time': get_eq_points(derived_jable, 'verification time', test_names,
                                            experiment_to_compare_against),
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
            f'Point given if at least {how_much_better * 100}% better than {experiment_to_compare_against}, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests)')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(graph_dir + f'{how_much_better * 100}%_better_points_compared_to_{experiment_to_compare_against}_{png_names[index]}.png', bbox_inches='tight')
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
            f'Point given if at least as good as {experiment_to_compare_against}, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests)')
        plt.xscale('log')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(graph_dir + f'better_or_eq_points_compared_to_{experiment_to_compare_against}_{png_names[index]}.png', bbox_inches='tight')
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