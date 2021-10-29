import copy
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    print(
        f"(time_size_avg_ratios) using ({experiment_to_compare_against_name}) results as numerator when computing size/time ratios")

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

    # Remove the rows
    # prev_sizes.drop(rows_to_delete, inplace=True)
    for data in data_list:
        data.drop(rows_to_delete, inplace=True)

    original_rules = ['rule A', 'rule B', 'rule C', 'rule D', 'rule E', 'rule F', 'rule G', 'rule H', 'rule I',
                      'rule J', 'rule K']

    def new_rule_used(row, new_rules):
        for rule in new_rules:
            if row[rule] > 0:
                return True
        return False

    def get_medians(data):
        rules_in_data = [column_name for column_name in data.columns if 'rule' in column_name]
        new_rules = [rule for rule in rules_in_data if rule not in original_rules]

        data_medians = dict()
        data_medians['overall_post_size_median'] = data.apply(
            lambda row: row['post place count'] + row['post transition count'],
            axis=1).median()

        try:
            data_medians['new_rules_post_size_median'] = data.apply(
                lambda row: (row['post place count'] + row['post transition count']) if new_rule_used(row,
                                                                                                      new_rules) else np.nan,
                axis=1).median()
        except:
            data_medians['new_rules_post_size_median'] = np.nan

        data_medians['no_new_rules_post_size_median'] = data.apply(
            lambda row: (row['post place count'] + row['post transition count']) if not new_rule_used(row,
                                                                                                      new_rules) else np.nan,
            axis=1).median()

        data_medians['overall_time_median'] = data['time'].median()

        try:
            data_medians['new_rules_time_median'] = data.apply(
                lambda row: row['time'] if new_rule_used(row, new_rules) else np.nan,
                axis=1).median()
        except:
            data_medians['new_rules_time_median'] = np.nan

        data_medians['no_new_rules_time_median'] = data.apply(
            lambda row: row['time'] if not new_rule_used(row, new_rules) else np.nan,
            axis=1).median()

        return data_medians

    # Get sizes from the data that will be used as numerator
    base_results_index = test_names.index(experiment_to_compare_against_name)
    base_results = data_list[base_results_index]
    base_results_medians = get_medians(base_results)

    data_list.pop(base_results_index)
    test_names.pop(base_results_index)
    combined = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list):

        data_medians = get_medians(data)

        ratios = dict()
        for key in base_results_medians.keys():
            base_value = base_results_medians[key]
            ratios[key] = (base_value / data_medians[key]) if data_medians[key] > 0 else np.nan

        df2 = pd.DataFrame(ratios,
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
        plt.savefig(graph_dir + f'median_ratios_{png_names[index]}_median_first.png', bbox_inches='tight')
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
