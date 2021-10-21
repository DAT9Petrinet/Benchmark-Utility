import os
import sys
import shutil

import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory_combined
import time_memory_lines
import reduction_points
import total_reductions
import time_size_ratios_lineplots
import time_size_avg_ratios
import rule_usage_absolute_models
import time_memory_points
import best_overall


def plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    """
    Will create all plots from all graph functions in this directory, except the deprecated ones
    """
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    graphs = [filename for filename in os.listdir(os.path.dirname(__file__)) if
              '.py' in filename and filename != 'all_graphs.py']
    num_graphs = len(graphs)
    graphs_made = 0

    # General graphs not fitting totally into the next categories
    answer_simplification_bars.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    best_overall.plot(data_list, test_names, graph_dir)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    # Plots that has to do with application of rules
    rule_usage_absolute.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    rule_usage_percentage.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    rule_usage_absolute_models.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    # Stuff to do with time and memory
    time_memory_combined.plot(data_list, test_names, graph_dir + '\\time-memory\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    metrics = ['time', 'memory']
    for metric in metrics:
        time_memory_lines.plot(data_list, test_names, graph_dir + '\\time-memory\\', metric)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_memory_points.plot(data_list, test_names, graph_dir + '\\time-memory\\', experiment_to_compare_against_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    # Stuff to do with reduction/size
    reduced_size.plot(data_list, test_names, graph_dir + '\\reductions\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    reduction_points.plot(data_list, test_names, graph_dir + '\\reductions\\', experiment_to_compare_against_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\')
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Stuff to do with ratios
    time_size_ratios_lineplots.plot(data_list, test_names, graph_dir + '\\size-ratios\\',
                                    experiment_to_compare_against_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")

    time_size_avg_ratios.plot(data_list, test_names, graph_dir + '\\size-ratios\\', experiment_to_compare_against_name)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs done")


if __name__ == "__main__":
    # Results used for comparisons in reduction_points plot
    if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]
        if experiment_to_compare_against_name == 'no-red':
            print('(reduction_points) Cannot use no-red as basis for comparison, as this has no reductions')

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    # Remove all graphs
    if os.path.isdir(graph_dir):
        shutil.rmtree(graph_dir)

    # Make new directories
    os.makedirs(graph_dir)
    os.makedirs(graph_dir + '\\rule-usage\\')
    os.makedirs(graph_dir + '\\size-ratios\\')
    os.makedirs(graph_dir + '\\reductions\\')
    os.makedirs(graph_dir + '\\time-memory\\')

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]
    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    try:
        pd.read_csv(csv_dir + experiment_to_compare_against_name + '.csv')
    except:
        raise Exception(
            f'(reduction_points) Could not find the file ({experiment_to_compare_against_name}). '
            f'Check if you made a typo in the parameter to the program')

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name)
