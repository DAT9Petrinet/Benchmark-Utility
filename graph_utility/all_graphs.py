import os
import sys
import copy
import pandas as pd
from os import walk

import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory


def main():
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Read csv data
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    # Call each graph function with relevant data
    answer_simplification_bars.plot(copy.deepcopy(data_list), test_names, graph_dir)
    print("1/5 graphs done")
    rule_usage_absolute.plot(copy.deepcopy(data_list), test_names, graph_dir)
    print("2/5 graphs done")
    rule_usage_percentage.plot(copy.deepcopy(data_list), test_names, graph_dir)
    print("3/5 graphs done")
    reduced_size.plot(copy.deepcopy(data_list), copy.deepcopy(test_names), graph_dir)
    print("4/5 graphs done")
    time_memory.plot(copy.deepcopy(data_list), test_names, graph_dir)
    print("5/5 graphs done")
    # Violin plots does not seem to make sense, might make sense on larger test-set, so I wont remove the files,
    # but I comment them out
    # violin_absolute.plot(copy.deepcopy(data_list), test_names, rules)
    # violin_percentage.plot(copy.deepcopy(data_list), test_names, rules)


if __name__ == "__main__":
    main()
