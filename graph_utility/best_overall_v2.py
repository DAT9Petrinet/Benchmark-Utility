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
        if test_name not in series or (test_name == 'no-red' and metric in ['reduce time', 'reduced size']):
            series[test_name] = 0
    return series


def second_smallest(list):
    return sorted(list)[1]


def get_strictly_better_points(derived_jable, metric, test_names):
    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    answer_columns = ([experiment_column + '@' + 'answer' for experiment_column in test_names])
    relevant_columns = metric_columns + answer_columns

    def find_best(row):
        s = second_smallest(row[metric_columns].values)
        return next(
            iter([experiment for experiment, value in row[metric_columns].items() if value <= 0.9 * s and row[
                experiment.split("@", 1)[0] + '@answer'] != 'NONE']),
            None)

    df = pd.DataFrame()
    df[metric + ' scores'] = derived_jable[relevant_columns].apply(
        find_best,
        axis=1)
    return zero_padding(df.value_counts(), metric, test_names).tolist()


def get_eq_points(derived_jable, metric, test_names):
    metric_columns = [experiment_column + '@' + metric for experiment_column in test_names]
    answer_columns = ([experiment_column + '@' + 'answer' for experiment_column in test_names])
    relevant_columns = metric_columns + answer_columns

    def equally_good_as_best(row, test, metric):
        s = second_smallest(row.values)
        return row[test + '@' + metric] <= s

    df = pd.DataFrame()
    for test in test_names:
        df[test + '@' + metric] = derived_jable[relevant_columns].apply(
            lambda row: 1 if equally_good_as_best(row[metric_columns], test, metric) and row[
                test + '@' + 'answer'] != 'NONE' else 0,
            axis=1)

    return zero_padding(df.sum(), metric, test_names).tolist()


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

    answer_df = get_answer_df(derived_jable, test_names)
    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': get_strictly_better_points(derived_jable, 'reduced size', test_names),
         'state space size': get_strictly_better_points(derived_jable, 'state space size', test_names),
         'reduce time': get_strictly_better_points(derived_jable, 'reduce time', test_names),
         'verification memory': get_strictly_better_points(derived_jable, 'verification memory', test_names),
         'verification time': get_strictly_better_points(derived_jable, 'verification time', test_names),
         'answered queries': answer_df,
         'unique answers': zero_padding(derived_jable['unique answers'].value_counts(), 'unique answers',
                                        test_names).tolist(),
         })

    points_eq_df = pd.DataFrame(
        {'reduced size': get_eq_points(derived_jable, 'reduced size', test_names),
         'state space size': get_eq_points(derived_jable, 'state space size', test_names),
         'reduce time': get_eq_points(derived_jable, 'reduce time', test_names),
         'verification memory': get_eq_points(derived_jable, 'verification memory', test_names),
         'verification time': get_eq_points(derived_jable, 'verification time', test_names),
         'answered queries': answer_df,
         })

    # Rename rows in the dataframe to be names of the experiments
    points_df = utility.rename_index_to_test_name(points_df, test_names)
    points_eq_df = utility.rename_index_to_test_name(points_eq_df, test_names)

    data_to_plot = utility.split_into_all_with_without(points_df)
    data_to_plot_eq = utility.split_into_all_with_without(points_eq_df)
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
