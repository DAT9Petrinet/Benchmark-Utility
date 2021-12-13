import copy
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility

REDUCE_TIMEOUT = 300


def get_points_by_metric(derived_jable, metric, test_names, experiment_to_compare_against, eq, how_much_better):
    def better_than_comparison(row, test, metric):
        if test == experiment_to_compare_against:
            return False
        if eq:
            return row[test + '@' + metric] <= row[experiment_to_compare_against + '@' + metric]
        else:
            if metric == 'reduced size':
                return row[test + '@' + metric] < (
                        (1 + how_much_better) * row[experiment_to_compare_against + '@' + metric])
            else:
                return row[test + '@' + metric] < (
                        (1 - how_much_better) * row[experiment_to_compare_against + '@' + metric])

    def equal_to_comparison(row, test, metric):
        if test == experiment_to_compare_against:
            return False
        return row[test + '@' + metric] == row[experiment_to_compare_against + '@' + metric]

    def point(row):
        if metric in ['verification time', 'verification memory', 'total time']:
            # Both got an answer
            if row[test + '@' + 'answer'] != 'NONE' and row[experiment_to_compare_against + '@' + 'answer'] != 'NONE':
                if better_than_comparison(row, test, metric):
                    return 1
                elif equal_to_comparison(row, test, metric):
                    return 0
                else:
                    return -1
            elif row[experiment_to_compare_against + '@' + 'answer'] != 'NONE':
                return -1
            elif row[test + '@' + 'answer'] != 'NONE':
                return 1
            elif row[test + '@' + 'answer'] == 'NONE' and row[experiment_to_compare_against + '@' + 'answer'] == 'NONE':
                return 0
            else:
                Exception("(better_than_x) should not be able to reach this - answer point")
        elif metric in ['state space size']:
            if row[experiment_to_compare_against + '@' + metric] != 0 and row[test + '@' + metric] != 0:
                if better_than_comparison(row, test, metric):
                    return 1
                elif equal_to_comparison(row, test, metric):
                    return 0
                else:
                    return -1
            elif row[experiment_to_compare_against + '@' + metric] != 0:
                return -1
            elif row[test + '@' + metric] != 0:
                return 1
            elif row[test + '@' + metric] == 0 and row[experiment_to_compare_against + '@' + metric] == 0:
                return 0
            else:
                Exception("(better_than_x) should not be able to reach this - state space size point")
        elif metric in ['reduce time']:
            if row[experiment_to_compare_against + '@' + metric] < REDUCE_TIMEOUT and row[
                test + '@' + metric] < REDUCE_TIMEOUT:
                if better_than_comparison(row, test, metric):
                    return 1
                elif equal_to_comparison(row, test, metric):
                    return 0
                else:
                    return -1
            elif row[experiment_to_compare_against + '@' + metric] < REDUCE_TIMEOUT:
                return -1
            elif row[test + '@' + metric] < REDUCE_TIMEOUT:
                return 1
            elif row[test + '@' + metric] < REDUCE_TIMEOUT and row[
                experiment_to_compare_against + '@' + metric] < REDUCE_TIMEOUT:
                return 0
            else:
                Exception("(better_than_x) should not be able to reach this - reduce time point")
        elif metric == 'reduced size':
            if utility.row_indicate_simplification_jable(row, experiment_to_compare_against) or \
                    utility.row_indicate_simplification_jable(row, test):
                return 0
            else:
                if better_than_comparison(row, test, metric):
                    return 1
                elif equal_to_comparison(row, test, metric):
                    return 0
                else:
                    return -1
        else:
            Exception("(better_than_x) should not be able to reach this - points")

    df = pd.DataFrame()
    for test in test_names:
        df[test + '@' + metric] = derived_jable.apply(
            point,
            axis=1)

    return utility.zero_padding(df.sum(), metric, test_names).tolist()


def get_answer_df(derived_jable, test_names):
    s = pd.Series(dtype=float)
    for test_name in test_names:
        s[test_name] = len(derived_jable[test_name + '@' + 'answer']) - (
            derived_jable[test_name + '@' + 'answer'].value_counts()['NONE'])

    return s.tolist()


def plot(data_list, test_names, graph_dir, experiment_to_compare_against, keep_largest_percent, how_much_better):
    if len(data_list) == 1:
        return

    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    data_list = utility.remove_errors_datalist(data_list)

    if len(test_names) == 2 and 'no-red' in test_names:
        print(
            '(best_overall) beware, probably weird results (in reduction points) in this graph due to comparing only 2 experiments, and one which is no-red')

    derived_jable = utility.make_derived_jable(data_list, test_names)
    derived_jable_sized = utility.largest_x_by_prev_size_jable(derived_jable, keep_largest_percent, test_names[0])

    answer_df = get_answer_df(derived_jable_sized, test_names)
    # Create a dataframe for each type of graph
    points_df = pd.DataFrame(
        {'reduced size': get_points_by_metric(derived_jable_sized, 'reduced size', test_names,
                                              experiment_to_compare_against, False, how_much_better),
         'state space size': get_points_by_metric(derived_jable_sized, 'state space size', test_names,
                                                  experiment_to_compare_against, False, how_much_better),
         'reduce time': get_points_by_metric(derived_jable_sized, 'reduce time', test_names,
                                             experiment_to_compare_against, False, how_much_better),
         'verification memory': get_points_by_metric(derived_jable_sized, 'verification memory', test_names,
                                                     experiment_to_compare_against, False, how_much_better),
         'verification time': get_points_by_metric(derived_jable_sized, 'verification time', test_names,
                                                   experiment_to_compare_against, False, how_much_better),
         'total time': get_points_by_metric(derived_jable_sized, 'total time', test_names,
                                            experiment_to_compare_against, False, how_much_better),
         'answered queries': answer_df,
         'unique answers': (utility.zero_padding(
             utility.unique_answers_comparison(derived_jable_sized, experiment_to_compare_against, test_names),
             'unique answers',
             test_names)).tolist(),
         }, index=test_names).drop('base-rules')

    if len(points_df) != 0:
        # Plot the plots
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = points_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.title(
            f'Point given if {how_much_better * 100}% better than {experiment_to_compare_against}, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests) by prev_size')
        plt.xscale('symlog')
        plt.xlabel("points")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

        plt.savefig(
            graph_dir + f'{how_much_better * 100}%_better_than_{experiment_to_compare_against}_largest_{keep_largest_percent * 100}%_tests_.png',
            bbox_inches='tight')
        plt.clf()

    if not os.path.isfile(
            graph_dir + f'eq_compare_to_{experiment_to_compare_against}_largest_{keep_largest_percent * 100}%_tests_all.png'):
        points_eq_df = pd.DataFrame(
            {'reduced size': get_points_by_metric(derived_jable_sized, 'reduced size', test_names,
                                                  experiment_to_compare_against,
                                                  True, how_much_better),
             'state space size': get_points_by_metric(derived_jable_sized, 'state space size', test_names,
                                                      experiment_to_compare_against, True, how_much_better),
             'reduce time': get_points_by_metric(derived_jable_sized, 'reduce time', test_names,
                                                 experiment_to_compare_against,
                                                 True, how_much_better),
             'verification memory': get_points_by_metric(derived_jable_sized, 'verification memory', test_names,
                                                         experiment_to_compare_against, True, how_much_better),
             'verification time': get_points_by_metric(derived_jable_sized, 'verification time', test_names,
                                                       experiment_to_compare_against, True, how_much_better),
             'total time': get_points_by_metric(derived_jable_sized, 'total time', test_names,
                                                experiment_to_compare_against, True, how_much_better),
             'answered queries': answer_df,
             }, index=test_names).drop('base-rules')

        if len(points_eq_df) != 0:
            # Plot the second plot with with
            plot = points_eq_df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))
            plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
            plt.title(
                f'Point given if at least as good as {experiment_to_compare_against}, using {keep_largest_percent * 100}% largest tests ({int(derived_jable.shape[0] * keep_largest_percent)} tests) by prev_size')
            plt.xscale('symlog')
            plt.xlabel("points")
            plt.ylabel('experiments')

            # Plot the numbers in the bars
            for p in plot.patches:
                left, bottom, width, height = p.get_bbox().bounds
                plot.annotate(int(width), xy=(left + width, bottom + height / 2), ha='center', va='center', size=10)

            plt.savefig(
                graph_dir + f'eq_compare_to_{experiment_to_compare_against}_largest_{keep_largest_percent * 100}%_tests.png',
                bbox_inches='tight')
            plt.clf()
