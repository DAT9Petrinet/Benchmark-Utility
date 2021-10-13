import os
import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory


def plot_all(data_list, test_names, graph_dir):
    # Call each graph function with relevant data
    answer_simplification_bars.plot(data_list, test_names, graph_dir)
    print("1/5 graphs done")
    rule_usage_absolute.plot(data_list, test_names, graph_dir)
    print("2/5 graphs done")
    rule_usage_percentage.plot(data_list, test_names, graph_dir)
    print("3/5 graphs done")
    reduced_size.plot(data_list, test_names, graph_dir)
    print("4/5 graphs done")
    time_memory.plot(data_list, test_names, graph_dir)
    print("5/5 graphs done")
    # Violin plots does not seem to make sense, might make sense on larger test-set, so I wont remove the files,
    # but I comment them out
    # violin_absolute.plot(copy.deepcopy(data_list), test_names, rules)
    # violin_percentage.plot(copy.deepcopy(data_list), test_names, rules)


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
