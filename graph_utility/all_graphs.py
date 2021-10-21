import os
import sys

import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory_combined
import time_memory
import reduction_points
import total_reductions
import rule_usage_absolute_models
import time_memory_points
import best_overall


def plot_all(data_list, test_names, graph_dir, correct_results_name):
    """
    Will create all plots from all graph functions in this directory, except the deprecated ones
    """
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    graphs = os.listdir(os.path.dirname(__file__))
    graphs.remove('size_ratio_deprecated.py')
    graphs.remove('__pycache__')
    graphs.remove('all_graphs.py')
    num_graphs = len(graphs)
    graphs_made = 0

    # Call each graph function with relevant data
    answer_simplification_bars.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    rule_usage_absolute.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    rule_usage_percentage.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    reduced_size.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    time_memory_combined.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    metrics = ['time', 'memory']
    for metric in metrics:
        time_memory.plot(data_list, test_names, graph_dir, metric)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    reduction_points.plot(data_list, test_names, graph_dir, correct_results_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    total_reductions.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    rule_usage_absolute_models.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    best_overall.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    time_memory_points.plot(data_list, test_names, graph_dir, correct_results_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")


if __name__ == "__main__":
    # Results used for comparisons in reduction_points plot
    if len(sys.argv) == 1:
        correct_results_name = 'base-rules'
    else:
        correct_results_name = sys.argv[1]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)
    else:
        for file in os.listdir(graph_dir):
            os.remove(os.path.join(graph_dir, file))

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]
    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    try:
        correct_results = pd.read_csv(csv_dir + correct_results_name + '.csv')
    except:
        raise Exception(
            f'(reduction_points)({correct_results_name}) is not present in saved/ and cannot be used as basis for comparison. '
            f'Check if you made a typo in the parameter to the program')

    plot_all(data_list, test_names, graph_dir, correct_results_name)
