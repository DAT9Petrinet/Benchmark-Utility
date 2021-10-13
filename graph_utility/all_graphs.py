import os
import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory
import time_lines
import memory


def plot_all(data_list, test_names, graph_dir):
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
    time_memory.plot(data_list, test_names, graph_dir)
    print(f"5/{num_graphs} graphs done")
    time_lines.plot(data_list, test_names, graph_dir)
    print(f"6/{num_graphs} graphs done")
    memory.plot(data_list, test_names, graph_dir)
    print(f"7/{num_graphs} graphs done")


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    csv_dir = os.path.join(script_dir, '..\saved\\')
    graph_dir = os.path.join(script_dir, '..\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]
    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in csvs]
    plot_all(data_list, test_names, graph_dir)
