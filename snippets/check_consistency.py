import sys
import os
import pandas as pd


def check_consistency():
    script_dir = os.path.dirname(__file__)
    result_dir = os.path.join(script_dir, '..\saved\\')

    # What we assume to be correct results
    correct_results_csv_name = 'base-rules.csv'
    correct_results_name = os.path.splitext(correct_results_csv_name)[0]
    correct_results = pd.read_csv(result_dir + correct_results_csv_name)

    # Read csv data
    paths = sys.argv[1:]
    data_list = [pd.read_csv(path) for path in paths]

    # Find names of the tests
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    print(f"Using {correct_results_name} as the basis for checking consitencies in our data\n")

    # Remove "correct_results_name" if present in argument list, as we assume this is correct anyways
    for index, test_name in enumerate(test_names):
        if correct_results_name == test_name:
            print(f"{correct_results_name}: trivially consistent \n")
            data_list.pop(index)
            test_names.pop(index)

    for test_index, data in enumerate(data_list):
        inconsistent_rows = []
        for index, row in data.iterrows():
            same_result = correct_results.iloc[index].answer == row.answer
            either_row_is_none = (correct_results.iloc[index].answer == 'NONE') or (row.answer == 'NONE')

            if (not same_result) and (not either_row_is_none):
                inconsistent_rows.append((correct_results.iloc[index], row))

        if len(inconsistent_rows) == 0:
            print(f"{test_names[test_index]} is consistent with {correct_results_name}\n")
        else:
            print(f"{test_names[test_index]} is not consistent with {correct_results_name}\n"
                  f"found inconsistencies in answers in: {len(inconsistent_rows)} rows\n")
            print(f"an example of this is the model/query combination:")
            print(f"{correct_results_name} output:")
            print(inconsistent_rows[0][0])
            print("")
            print(f"{test_names[test_index]} output:")
            print(inconsistent_rows[0][1])
            print("--------------------------------------------------------------------")


if __name__ == '__main__':
    check_consistency()
