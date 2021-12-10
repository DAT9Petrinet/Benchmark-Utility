import os
import sys

import numpy as np
import pandas as pd


def check_consistency(correct_results, correct_results_name, data_list, test_names, matrix):
    matrix_dict = dict()

    if not matrix:
        print(f"Using {correct_results_name} as the basis for checking consistencies in our data")
        print("--------------------------------------------------------------------")

        # Remove "correct_results_name" if present in argument list, as we assume this is correct anyways
        for index, test_name in enumerate(test_names):
            if correct_results_name == test_name:
                print(f"{correct_results_name}: trivially consistent \n")
                data_list.pop(index)
                test_names.pop(index)

    for test_index, data in enumerate(data_list):
        if matrix:
            if test_names[test_index] == correct_results_name:
                matrix_dict[test_names[test_index]] = 0
                continue
            elif test_index < test_names.index(correct_results_name):
                matrix_dict[test_names[test_index]] = np.nan
                continue
        inconsistent_rows = []
        for index, row in data.iterrows():
            same_result = correct_results.iloc[index].answer == row.answer
            either_row_is_none = (correct_results.iloc[index].answer == 'NONE') or (row.answer == 'NONE')

            if (not same_result) and (not either_row_is_none):
                inconsistent_rows.append((correct_results.iloc[index], row))

        if not matrix:
            if len(inconsistent_rows) == 0:
                print(f"{test_names[test_index]} is consistent with {correct_results_name}\n")
                print("--------------------------------------------------------------------")
            else:
                print(f"({test_names[test_index]}) is not consistent with ({correct_results_name})\n"
                      f"Found inconsistencies in answers in: {len(inconsistent_rows)} rows\n")
                print(f"First instance found of an inconsistency is the model/query combination:")
                print(f"({correct_results_name}) output:")
                print(inconsistent_rows[0][0])
                print("")
                print(f"({test_names[test_index]}) output:")
                print(inconsistent_rows[0][1])
                print("--------------------------------------------------------------------")
        else:
            matrix_dict[test_names[test_index]] = int(len(inconsistent_rows))

    if not matrix:
        print("Done checking for consistency")
    else:
        return matrix_dict


if __name__ == "__main__":
    # What we assume to be correct results
    if len(sys.argv) == 1:
        correct_results_name = 'base-rules'
        matrix = False
    else:
        correct_results_name = sys.argv[1]
        if correct_results_name == 'matrix':
            matrix = True
        else:
            matrix = False

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '../results\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if ('.csv' in file) and (correct_results_name not in file)]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    if not matrix:
        try:
            correct_results = pd.read_csv(csv_dir + correct_results_name + '.csv')
        except:
            raise Exception(
                f'({correct_results_name}) is not present in results/ and cannot be used as basis for comparison. '
                f'Check if you made a typo in the parameter to the program')

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    if not matrix:
        check_consistency(correct_results, correct_results_name, data_list, test_names, matrix)
    else:
        matrix_df = pd.DataFrame()
        for index, correct_results in enumerate(data_list):
            row = check_consistency(correct_results, test_names[index], data_list, test_names, matrix)
            matrix_df = matrix_df.append(row, ignore_index=True)

        new_rows_indices = dict()
        for index, name in enumerate(test_names):
            new_rows_indices[index] = name
        matrix_df = matrix_df.rename(index=new_rows_indices)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        print(matrix_df)
