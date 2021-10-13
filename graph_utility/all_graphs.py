import os
import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory_combined
import time_memory


def plot_all(data_list, test_names, graph_dir):
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

    # Call each graph function with relevant data
    answer_simplification_bars.plot(data_list, test_names, graph_dir)
    print(f"1/{num_graphs} graphs done")
    rule_usage_absolute.plot(data_list, test_names, graph_dir)
    print(f"2/{num_graphs} graphs done")
    rule_usage_percentage.plot(data_list, test_names, graph_dir)
    print(f"3/{num_graphs} graphs done")
    reduced_size.plot(data_list, test_names, graph_dir)
    print(f"4/{num_graphs} graphs done")
    time_memory_combined.plot(data_list, test_names, graph_dir)
    print(f"5/{num_graphs} graphs done")
    metrics = ['time', 'memory']
    for metric in metrics:
        time_memory.plot(data_list, test_names, graph_dir, metric)
    print(f"6/{num_graphs} graphs done")


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]
    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    plot_all(data_list, test_names, graph_dir)
