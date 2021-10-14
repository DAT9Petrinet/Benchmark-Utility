import sys
import os
import pandas as pd


def check_consistency(correct_results, correct_results_name, data_list, test_names):
    print(f"Using {correct_results_name} as the basis for checking consistencies in our data")
    print("--------------------------------------------------------------------")

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
            print(f"({test_names[test_index]}) is not consistent with ({correct_results_name})\n"
                  f"Found inconsistencies in answers in: {len(inconsistent_rows)} rows\n")
            print(f"First instance found of an inconsistency is the model/query combination:")
            print(f"({correct_results_name}) output:")
            print(inconsistent_rows[0][0])
            print("")
            print(f"({test_names[test_index]}) output:")
            print(inconsistent_rows[0][1])
            print("--------------------------------------------------------------------")


if __name__ == "__main__":
    # What we assume to be correct results
    correct_results_name = sys.argv[1]

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if ('.csv' in file) and (correct_results_name not in file)]
    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]
    correct_results = pd.read_csv(csv_dir + correct_results_name + '.csv')

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    check_consistency(correct_results, correct_results_name, data_list, test_names)
