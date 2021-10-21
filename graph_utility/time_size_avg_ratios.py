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
                raise Exception('(size_time_ratio) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                base_reduction_size = base_results_row['post place count'] + base_results_row['post transition count']
                size_post_reductions = row['post place count'] + row['post transition count']

                try:
                    size_ratio = (base_reduction_size / size_post_reductions)
                except:
                    size_ratio = np.nan
                time_ratio = (base_results_row['time'] / row['time'])

                if new_rule_used:
                    size_ratios_inner.append(size_ratio)
                    time_ratios_inner.append(time_ratio)
                else:
                    not_used_size_ratios_inner.append(size_ratio)
                    not_used_time_ratios_inner.append(time_ratio)

        # Add ratios to the current dataframe, with the tests being compared as the column name
        rule_used_size = sum(size_ratios_inner) / len(
            size_ratios_inner) if len(size_ratios_inner) > 0 else np.nan
        rule_used_time = sum(time_ratios_inner) / len(
            time_ratios_inner) if len(time_ratios_inner) > 0 else np.nan
        rule_not_used_size = sum(not_used_size_ratios_inner) / len(
            not_used_size_ratios_inner) if len(not_used_size_ratios_inner) > 0 else np.nan
        rule_not_used_time = sum(not_used_time_ratios_inner) / len(
            not_used_time_ratios_inner) if len(not_used_time_ratios_inner) > 0 else np.nan
        both_size = (sum(not_used_size_ratios_inner) + sum(size_ratios_inner)) / (
                len(not_used_size_ratios_inner) + len(size_ratios_inner))
        both_time = (sum(not_used_time_ratios_inner) + sum(time_ratios_inner)) / (
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
        # Plot the plot
        plot = data.plot(kind='barh', width=0.8, linewidth=2, figsize=(10, 10))

        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

        plt.xlabel("ratio")
        plt.ylabel('experiments')

        # Find max width, in order to move the very small numbers away from the bars
        max_width = 0
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            max_width = max(width, max_width)
        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            if width < (max_width / 10):
                plot.annotate(format(width, '.2f'), xy=(max_width / 12.5, bottom + height / 2),
                              ha='center', va='center')
            else:
                plot.annotate(format(width, '.2f'), xy=(left + width / 2, bottom + height / 2),
                              ha='center', va='center')

        plt.savefig(graph_dir + f'avg_ratios_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            ('.csv' in file) and (experiment_to_compare_against_name not in file)]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    try:
        correct_results = pd.read_csv(csv_dir + experiment_to_compare_against_name + '.csv')
    except:
        raise Exception(
            f'(reduction_points)({experiment_to_compare_against_name}) is not present in saved/ and cannot be used as basis for comparison. '
            f'Check if you made a typo in the parameter to the program')

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir, experiment_to_compare_against_name)
