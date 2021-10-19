import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import copy


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    print(f"(size_time_ratio) Comparing reduced size with ({experiment_to_compare_against_name})")
    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    pd.set_option('display.max_rows', None)

    # Remove test with no reduction
    for index, name in enumerate(test_names):
        if 'no-red' in name:
            data_list.pop(index)
            test_names.pop(index)

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

    # Dataframe to hold the size ratio between reduced nets
    size_ratios = pd.DataFrame()
    time_ratios = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list):
        # Dont compare size against the numerator, would just be 1 and a quite boring line
        if test_index == base_results_index:
            continue

        size_ratios_inner = pd.DataFrame()
        time_ratios_inner = pd.DataFrame()
        # Iterate through all rows and compute ratio
        for index, row in data.iterrows():
            base_results_row = base_results.loc[index]

            # Sanity check
            if (base_results_row['model name'] != row['model name']) or (
                    base_results_row['query index'] != row['query index']):
                raise Exception('(size_time_ratio) Comparing wrong rows')

            if (base_results_row['answer'] != 'NONE') and row['answer'] != 'NONE':
                base_reduction_size = base_results_row['post place count'] + base_results_row['post transition count']
                size_post_reductions = row['post place count'] + row['post transition count']

                size_ratio = (base_reduction_size / size_post_reductions) * 100
                size_ratios_inner = size_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)

                time_ratio = (base_results_row['time'] / row['time']) * 100
                time_ratios_inner = time_ratios_inner.append(pd.Series(data={'ratio': time_ratio}, name=index),
                                                             ignore_index=False)
            elif (base_results_row['answer'] == 'NONE') and row['answer'] != 'NONE':
                size_ratio = np.nan
                size_ratios_inner = size_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
                time_ratios_inner = time_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
            elif (base_results_row['answer'] != 'NONE') and row['answer'] == 'NONE':
                size_ratio = np.infty
                size_ratios_inner = size_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
                time_ratios_inner = time_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
            elif (base_results_row['answer'] == 'NONE') and row['answer'] == 'NONE':
                size_ratio = np.infty
                size_ratios_inner = size_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
                time_ratios_inner = time_ratios_inner.append(pd.Series(data={'ratio': size_ratio}, name=index),
                                                             ignore_index=False)
            else:
                raise Exception(
                    '(size_time_ratio) Should not be able to reach this. '
                    'Something went wrong with the checks for "NONE"')

        # Add ratios to the current dataframe, with the tests being compared as the column name
        size_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = size_ratios_inner.sort_values(
            'ratio').reset_index().drop(
            columns=
            'index')

        time_ratios[
            f"{experiment_to_compare_against_name}/{test_names[test_index]}"] = time_ratios_inner.sort_values(
            'ratio').reset_index().drop(
            columns=
            'index')

    # Make sure colors and dashes matches the ones from 'time_memory_combined'
    def color(t):
        a = np.array([0.5, 0.5, 0.5])
        b = np.array([0.5, 0.5, 0.5])
        c = np.array([1.0, 1.0, 1.0])
        d = np.array([0.0, 0.33, 0.67])

        return a + (b * np.cos(2 * np.pi * (c * t + d)))

    sns.set_theme(style="darkgrid")
    custom_palette = {}

    for column_index, column in enumerate(size_ratios.columns):
        custom_palette[column] = color((column_index + 1) / len(size_ratios.columns))

    # plot the plot
    sns.lineplot(data=size_ratios, palette=custom_palette).set(xlabel='test instance', ylabel='size ratio',
                                                               yscale="log",
                                                               title=f'Reduced size of nets compared to {experiment_to_compare_against_name}, '
                                                                     f'under 100 means {experiment_to_compare_against_name} is better')
    plt.savefig(graph_dir + 'reduced_size_compared.png')
    plt.clf()

    # plot the plot
    sns.lineplot(data=time_ratios, palette=custom_palette).set(xlabel='test instance', ylabel='time in seconds',
                                                               yscale="log",
                                                               title=f'Time compared to {experiment_to_compare_against_name}, '
                                                                     f'under 100 means {experiment_to_compare_against_name} is better')
    plt.savefig(graph_dir + 'time_compared.png')
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
