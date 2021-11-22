import os
import sys

import numpy as np
import pandas as pd


def check_consistency(exp_1, exp_1_name, data_list, test_names, consistency_dir):
    matrix_dict = dict()

    for test_index, data in enumerate(data_list):
        if test_names[test_index] == exp_1_name:
            matrix_dict[test_names[test_index]] = np.nan
            continue
        elif test_index < test_names.index(exp_1_name):
            matrix_dict[test_names[test_index]] = np.nan
            continue
        inconsistent_rows = []
        for index, row in data.iterrows():
            same_result = exp_1.iloc[index].answer == row.answer
            either_row_is_none = (exp_1.iloc[index].answer == 'NONE') or (row.answer == 'NONE')

            if (not same_result) and (not either_row_is_none):
                inconsistent_rows.append((exp_1.iloc[index], row))

        num_consistent_rows = int(len(inconsistent_rows))
        matrix_dict[test_names[test_index]] = num_consistent_rows
        if num_consistent_rows > 0:
            inconsistent_rows_df = pd.DataFrame()
            for inconsistent_row in inconsistent_rows:
                df = pd.Series(dtype=float)
                for i in range(2):
                    if i == 0:
                        inconsistent_row_appended = inconsistent_row[i].add_prefix(exp_1_name + '@')
                    else:
                        inconsistent_row_appended = inconsistent_row[i].add_prefix(test_names[test_index] + '@')
                    df = df.append(inconsistent_row_appended)
                inconsistent_rows_df = inconsistent_rows_df.append(df, ignore_index=True)
            inconsistent_rows_df.to_csv(
                f'{consistency_dir}/inconsistent_rows_({exp_1_name})_({test_names[test_index]}).csv')

    return matrix_dict


if __name__ == "__main__":

    if len(sys.argv) > 1:
        experiment_path = sys.argv[1]
    else:
        experiment_path = 'saved/'

    print(f"(check_consistency) using experiments in {experiment_path} to check consistency")
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)

    # Directory for all our csv
    test_dir = os.path.join(script_dir, f'..\\{experiment_path}')

    consistency_dir = os.path.join(script_dir, "../saved/consistency")

    # Read csv data
    csvs = [file for file in os.listdir(test_dir) if ('.csv' in file)]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(test_dir + csv) for csv in csvs]

    if not os.path.isdir(consistency_dir):
        os.makedirs(consistency_dir)

    matrix_df = pd.DataFrame()
    for index, exp_1 in enumerate(data_list):
        row = check_consistency(exp_1, test_names[index], data_list, test_names, consistency_dir)
        matrix_df = matrix_df.append(row, ignore_index=True)

    new_rows_indices = dict()
    for index, name in enumerate(test_names):
        new_rows_indices[index] = name
    matrix_df = matrix_df.rename(index=new_rows_indices)
    matrix_df.to_csv(f'{consistency_dir}/matrix.csv')
