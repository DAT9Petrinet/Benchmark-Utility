import sys
import os
import pandas as pd


def check_consistency():
    script_dir = os.path.dirname(__file__)
    result_dir = os.path.join(script_dir, '..\saved\\')
    correct_results_csv_name = 'base-rules.csv'

    # What we assume to be correct results
    correct_results = pd.read_csv(result_dir+correct_results_csv_name)

    # Read csv data
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    # Remove "base-rules" if present in argument list, as we assume this is correct anyways
    for index, test_name in enumerate(test_names):
        if 'base-rules' in test_name:
            data_list.pop(index)
            test_names.pop(index)

    for data in data_list:
        for index, row in data.iterrows():
            





if __name__ == '__main__':
    check_consistency()
