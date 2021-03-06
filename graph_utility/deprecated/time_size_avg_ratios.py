import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import utility


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    print(
        f"(time_size_avg_ratios) using ({experiment_to_compare_against_name}) results as numerator when computing size/time ratios")

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Find test instances that no experiment managed to reduce
    data_list = utility.filter_out_test_instances_that_were_not_reduced_by_any(data_list)

    # Get sizes from the data that will be used as numerator
    base_results_index = test_names.index(experiment_to_compare_against_name)
    base_results = data_list[base_results_index]
    data_list.pop(base_results_index)
    test_names.pop(base_results_index)

    # The original rules, which we will not use as new rules
    original_rules = ['rule A', 'rule B', 'rule C', 'rule D', 'rule E', 'rule F', 'rule G', 'rule H', 'rule I',
                      'rule J', 'rule K']

    # Dataframe to hold the size ratio between reduced nets
    combined = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list):
        # Find new rules in this experiment
        rules_in_data = [column_name for column_name in data.columns if 'rule' in column_name]
        new_rules = [rule for rule in rules_in_data if rule not in original_rules]

        size_ratios_inner = []
        time_ratios_inner = []
        not_used_size_ratios_inner = []
        not_used_time_ratios_inner = []
        # Iterate through all rows and compute ratio
        for index, row in data.iterrows():

            new_rule_used = False
            for rule in new_rules:
                if row[rule] > 0:
                    new_rule_used = True

            # Now we are only dealing with rows, where a new rule has been applied
            base_results_row = base_results.loc[index]

            # Sanity check
            if (base_results_row['model name'] != row['model name']) or (
                    base_results_row['query index'] != row['query index']):
                raise Exception('(time_size_avg_ratios) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                base_reduction_size = base_results_row['post place count'] + base_results_row['post transition count']
                size_post_reductions = row['post place count'] + row['post transition count']

                if size_post_reductions == 0:
                    size_ratio = np.nan
                elif size_post_reductions >= 1:
                    size_ratio = (base_reduction_size / size_post_reductions)
                else:
                    raise Exception('(time_size_avg_ratios) Something went wrong with calculating size')

                try:
                    time_ratio = (base_results_row['verification time'] / row['verification time'])
                except:
                    time_ratio = np.nan

                if new_rule_used:
                    size_ratios_inner.append(size_ratio)
                    time_ratios_inner.append(time_ratio)
                else:
                    not_used_size_ratios_inner.append(size_ratio)
                    not_used_time_ratios_inner.append(time_ratio)

        # Add ratios to the current dataframe, with the tests being compared as the column name
        rule_used_size = np.nansum(size_ratios_inner) / len(
            size_ratios_inner) if len(
            size_ratios_inner) else np.nan
        rule_used_time = np.nansum(time_ratios_inner) / len(
            time_ratios_inner) if len(
            time_ratios_inner) else np.nan
        rule_not_used_size = np.nansum(not_used_size_ratios_inner) / len(
            not_used_size_ratios_inner) if len(not_used_size_ratios_inner) else np.nan
        rule_not_used_time = np.nansum(not_used_time_ratios_inner) / len(
            not_used_time_ratios_inner) if len(not_used_time_ratios_inner) else np.nan
        both_size = (np.nansum(not_used_size_ratios_inner) + np.nansum(size_ratios_inner)) / (
                len(not_used_size_ratios_inner) + len(size_ratios_inner))
        both_time = (np.nansum(not_used_time_ratios_inner) + np.nansum(time_ratios_inner)) / (
                len(not_used_time_ratios_inner) + len(time_ratios_inner))

        df2 = pd.DataFrame(
            [[rule_used_size, rule_used_time, rule_not_used_size, rule_not_used_time, both_size, both_time]],
            columns=['size ratio when using new rules', 'time ratio when using new rules',
                     'size ratio when not using new rules',
                     'time ratio when not using new rules', 'overall size ratio',
                     'overall time ratio'],
            index=[f'{experiment_to_compare_against_name}/{test_names[test_index]}'])

        combined = combined.append(df2)

    columns_with_with = [f'{experiment_to_compare_against_name}/' + test_name for test_name in test_names if
                         "with" in test_name]
    columns_not_with_with = [f'{experiment_to_compare_against_name}/' + test_name for test_name in test_names if
                             "with" not in test_name]

    combined_with_with = combined.drop(columns_not_with_with)
    combined_without_with = combined.drop(columns_with_with)

    data_to_plot = [combined, combined_with_with, combined_without_with]
    png_names = ['all', 'with', 'without']

    sns.set_theme(style="darkgrid", palette="pastel")
    for index, data in enumerate(data_to_plot):
        if len(data) == 0:
            continue
        # Plot the plot
        plot = data.plot(kind='barh', width=0.8, linewidth=2, figsize=(10, 10))
        plt.axvline(x=1, color='r', lw=4)
        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

        plt.xlabel("ratio")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            if width > 0:
                plot.annotate(format(width, '.2f'), xy=(left + width, bottom + height / 2), ha='center', va='center',
                              size=10)
        plt.savefig(graph_dir + f'avg_ratios_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) <= 2:
        raise Exception(
            f'(time_memory_points) You need to specify more than one csv, the first will be used as basis for comparison')
    else:
        experiment_to_compare_against_name = [os.path.split(os.path.splitext(sys.argv[1])[0])[1]][0]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\time-memory\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
