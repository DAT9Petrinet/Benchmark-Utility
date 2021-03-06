import os
import shutil
import sys
import tkinter as tk
from glob import glob

import numpy as np
import pandas as pd


def gui():
    DIR = 'P10'
    BACKGROUND = '#C0C0C0'
    FOREGROUND = '#1923E8'
    master = tk.Tk()
    master.configure(bg=BACKGROUND)
    master.title(f'Select files in /{DIR} to use for consistency')
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, '..\\results\\')
    all_csv_files = [file.split('results')[1]
                     for path, subdir, files in os.walk(results_dir)
                     for file in glob(os.path.join(path, "*.csv"))]
    results = {}
    row = 0
    column = 0
    previous_top = ''
    previous_level = 0
    max_row = 0
    for f in all_csv_files:
        if DIR not in f:
            continue
        f = f.replace(f'\\{DIR}', '')
        level = (f.count('\\'))
        if level > 1:
            if column == 0:
                row = 0
                column = 1
            current_top = f.split('\\')[1]
            if previous_top != '' and previous_top != current_top:
                column += 1
                row = 0
            if level > previous_level and previous_top == current_top:
                column += 1
            previous_top = current_top

        var = tk.IntVar()
        if level == 1 and 'base-rules' in f:
            var.set(1)
        tk.Checkbutton(master, text=f, variable=var, bg=BACKGROUND, fg=FOREGROUND).grid(row=row, column=column)
        results[f] = var

        previous_level = level
        row += 1
        if row > max_row:
            max_row = row

    tk.Button(master, text="Select", command=master.destroy, bg=BACKGROUND, fg=FOREGROUND).grid(row=0,
                                                                                                column=column +1)
    tk.Button(master, text="Exit", command=sys.exit, bg=BACKGROUND, fg=FOREGROUND).grid(row=1,
                                                                                        column=column +1)
    master.mainloop()

    chosen_results = [csv_name for csv_name in results.keys() if '.csv' in csv_name and results[csv_name].get() == 1]

    category = chosen_results[0].split('\\')[1]
    for index, result in enumerate(chosen_results):
        curr_category = result.split('\\')[1]
        if curr_category != category:
            raise Exception(f'Comparing across categories {category} and {curr_category}')
        chosen_results[index] = f'\\{DIR}\\{result}'

    if len(chosen_results) == 0:
        raise Exception('You did not choose any experiment')

    return chosen_results, category


def check_consistency(exp_1, exp_1_name, data_list, test_names, consistency_dir, category):
    matrix_dict = dict()

    for test_index, data in enumerate(data_list):
        if test_names[test_index] == exp_1_name:
            matrix_dict[test_names[test_index]] = np.nan
            continue
        elif test_index < test_names.index(exp_1_name):
            matrix_dict[test_names[test_index]] = np.nan
            continue

        combined = exp_1.merge(data, left_index=True, right_index=True)
        combined = combined.loc[~(combined[f"{test_names[test_index]}@answer"] == combined[f"{exp_1_name}@answer"])]
        num_consistent_rows = int(len(combined))
        matrix_dict[test_names[test_index]] = num_consistent_rows
        if num_consistent_rows > 0:
            combined.to_csv(
                f'{consistency_dir}/inconsistent_rows_({exp_1_name})_({test_names[test_index]})_{category}.csv')

    return matrix_dict


if __name__ == "__main__":

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, '..\\results')

    consistency_dir = (results_dir + '\\consistency')

    # Remove all graphs
    if os.path.isdir(consistency_dir):
        shutil.rmtree(consistency_dir)

    os.makedirs(consistency_dir)

    # Read csv data
    csvs, category = gui()

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]
    print(f"(check_consistency) using experiments to check consistency: {test_names}")

    data_list = [pd.read_csv(results_dir + csv) for csv in csvs]
    for i, data in enumerate(data_list):
        data.drop(data.index[data['answer'] == 'NONE'], inplace=True)
        data.set_index(["model name", "query index"], inplace=True)
        data.rename(columns={col: f"{test_names[i]}@{col}" for col in data.columns}, inplace=True)

    matrix_df = pd.DataFrame()
    for index, exp_1 in enumerate(data_list):
        row = check_consistency(exp_1, test_names[index], data_list, test_names, consistency_dir, category)
        matrix_df = matrix_df.append(row, ignore_index=True)

    new_rows_indices = dict()
    for index, name in enumerate(test_names):
        new_rows_indices[index] = name
    matrix_df = matrix_df.rename(index=new_rows_indices)
    matrix_df.to_csv(f'{consistency_dir}/matrix_{category}.csv')
    print("Done")
