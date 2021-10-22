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
        f"(time_size_ratios_lineplots) using ({experiment_to_compare_against_name}) results as numerator when computing size/time ratios")

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

    # Get sizes from the data that will be used as numerator
    base_results_index = test_names.index(experiment_to_compare_against_name)
    base_results = data_list[base_results_index]
    data_list.pop(base_results_index)
    test_names.pop(base_results_index)

    # Find the rules that we have implemented, that the basis for comparison does not use
    base_results_rules = [column_name for column_name in base_results.columns if 'rule' in column_name]
    original_rules = ['rule A', 'rule B', 'rule C', 'rule D', 'rule E', 'rule F', 'rule G', 'rule H', 'rule I',
                      'rule J', 'rule K']

    # Find the rules that the base_result do not use (that is not part of the original rules)
    rule_usage_summed = base_results[base_results_rules].agg('sum')
    non_used_rules = [key for key in rule_usage_summed.keys() if rule_usage_summed.get(key) == 0]
    base_results_non_used_new_rules = [rules for rules in non_used_rules if rules not in original_rules]

    # Dataframe to hold the size ratio between reduced nets
    rule_used_size_ratios = pd.DataFrame()
    rule_used_time_ratios = pd.DataFrame()
    rule_not_used_size_ratios = pd.DataFrame()
    rule_not_used_time_ratios = pd.DataFrame()
    rule_indifferent_size_ratios = pd.DataFrame()
    rule_indifferent_time_ratios = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list):
        rules_in_data = [column_name for column_name in data.columns if 'rule' in column_name]
        new_rules = [rules for rules in rules_in_data if rules not in original_rules]

        rule_used_size_ratios_inner = []
        rule_used_time_ratios_inner = []
        rule_not_used_size_ratios_inner = []
        rule_not_used_time_ratios_inner = []
        rule_indifferent_size = []
        rule_indifferent_time = []

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
                raise Exception('(size_time_ratio) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                base_reduction_size = base_results_row['post place count'] + base_results_row['post transition count']
                size_post_reductions = row['post place count'] + row['post transition count']

                try:
                    size_ratio = (base_reduction_size / size_post_reductions)
                except:
                    size_ratio = np.nan
                time_ratio = (base_results_row['time'] / row['time'])

                rule_indifferent_size.append(size_ratio)
                rule_indifferent_time.append(time_ratio)
                if new_rule_used:
                    rule_used_size_ratios_inner.append(size_ratio)
                    rule_used_time_ratios_inner.append(time_ratio)
                    rule_not_used_size_ratios_inner.append(np.nan)
                    rule_not_used_time_ratios_inner.append(np.nan)
                else:
                    rule_used_size_ratios_inner.append(np.nan)
                    rule_used_time_ratios_inner.append(np.nan)
                    rule_not_used_size_ratios_inner.append(size_ratio)
                    rule_not_used_time_ratios_inner.append(time_ratio)
            else:
                ratio = np.nan
                rule_indifferent_size.append(ratio)
                rule_indifferent_time.append(ratio)
                rule_used_size_ratios_inner.append(ratio)
                rule_used_time_ratios_inner.append(ratio)
                rule_not_used_size_ratios_inner.append(ratio)
                rule_not_used_time_ratios_inner.append(ratio)

        # Add ratios to the current dataframe, with the tests being compared as the column name
        rule_used_size_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_used_size_ratios_inner)

        rule_used_time_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_used_time_ratios_inner)

        rule_not_used_size_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_not_used_size_ratios_inner)

        rule_not_used_time_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_not_used_time_ratios_inner)

        rule_indifferent_size_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_indifferent_size)

        rule_indifferent_time_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = np.sort(rule_indifferent_time)

    size_ratio_dfs = [rule_used_size_ratios, rule_not_used_size_ratios, rule_indifferent_size_ratios]
    time_ratio_dfs = [rule_used_time_ratios, rule_not_used_time_ratios, rule_indifferent_time_ratios]

    png_names = ['new_rules', 'not_new_rules', 'all']

    # Make sure colors and dashes matches the ones from 'time_memory_combined'
    def color(t):
        a = np.array([0.5, 0.5, 0.5])
        b = np.array([0.5, 0.5, 0.5])
        c = np.array([1.0, 1.0, 1.0])
        d = np.array([0.0, 0.33, 0.67])

        return a + (b * np.cos(2 * np.pi * (c * t + d)))

    sns.set_theme(style="darkgrid")
    custom_palette = {}

    for column_index, column in enumerate(rule_used_size_ratios.columns):
        custom_palette[column] = color((column_index + 1) / len(rule_used_size_ratios.columns))

    for i in range(3):
        # plot the plot
        sns.lineplot(data=size_ratio_dfs[i], palette=custom_palette).set(xlabel='test instance', ylabel='size ratio',
                                                                         yscale="log",
                                                                         title=f'Reduced size of nets compared to {experiment_to_compare_against_name}, '
                                                                               f'under 1 means {experiment_to_compare_against_name} is better')
        plt.savefig(graph_dir + f'{png_names[i]}_used_size_ratios.png')
        plt.clf()

        # plot the plot
        sns.lineplot(data=time_ratio_dfs[i], palette=custom_palette).set(xlabel='test instance',
                                                                         ylabel='time ratio',
                                                                         yscale="log",
                                                                         title=f'Time compared to {experiment_to_compare_against_name}, '
                                                                               f'under 1 means {experiment_to_compare_against_name} is better')
        plt.savefig(graph_dir + f'{png_names[i]}_used_time_ratios.png')
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
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\size-ratios\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            ('.csv' in file) and (experiment_to_compare_against_name not in file)]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
