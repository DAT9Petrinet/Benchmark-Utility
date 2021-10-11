import sys
import os
import pandas as pd


def check_consistency():
    script_dir = os.path.dirname(__file__)
    result_dir = os.path.join(script_dir, '..\saved\\')
    correct_results_csv_name = 'base-rules.csv'
    correct_results_name = os.path.splitext(correct_results_csv_name)[0]

    # What we assume to be correct results
    correct_results = pd.read_csv(result_dir + correct_results_csv_name)

    # Read csv data
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    # Remove "base-rules" if present in argument list, as we assume this is correct anyways
    for index, test_name in enumerate(test_names):
        if correct_results_name == test_name:
            print(f"{correct_results_name}: trivially consistent \n")
            data_list.pop(index)
            test_names.pop(index)

    for test_index, data in enumerate(data_list):
        found_inconsistency = False
        for index, row in data.iterrows():
            same_result = correct_results.iloc[index].answer == row.answer
            either_row_is_none = (correct_results.iloc[index].answer == 'NONE') or (row.answer == 'NONE')

            if (not same_result) and (not either_row_is_none):
                found_inconsistency = True
                print(f"{test_names[test_index]} is not consistent with {correct_results_name}")
                print(
                    f"The rows from ({correct_results_name}) and ({test_names[test_index]}) where the answer diverged:")
                print(f"The row from ({correct_results_name})")
                print(correct_results.iloc[index])
                print("")
                print(f"The row from ({test_names[test_index]})")
                print(row)
                print("")
                break

        if found_inconsistency:
            continue
        print(f"{test_names[test_index]} is consistent with {correct_results_name}\n")


if __name__ == '__main__':
    check_consistency()
