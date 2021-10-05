import os
import sys
import copy

import pandas as pd
import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import size_ratio
import time_memory
import violin_plot_absolute
import violin_plot_percentage


def main():
    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]
    data_list = [pd.read_csv(path) for path in paths]
    rules = [column for column in (pd.read_csv(paths[0], index_col=0, nrows=0).columns.tolist()) if "rule" in column]
    unneeded_columns_for_size_ratio = [column for column in
                                       (pd.read_csv(paths[0], index_col=0, nrows=0).columns.tolist()) if
                                       not (("place" in column) or ("transition" in column))]

    answer_simplification_bars.plot(copy.deepcopy(data_list), test_names)
    rule_usage_absolute.plot(copy.deepcopy(data_list), test_names, rules)
    rule_usage_percentage.plot(copy.deepcopy(data_list), test_names, rules)
    size_ratio.plot(copy.deepcopy(data_list), test_names, unneeded_columns_for_size_ratio)
    time_memory.plot(copy.deepcopy(data_list), test_names)
    violin_plot_absolute.plot(copy.deepcopy(data_list), test_names, rules)
    violin_plot_percentage.plot(copy.deepcopy(data_list), test_names, rules)


if __name__ == "__main__":
    main()