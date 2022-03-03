import os
import shutil
import sys
import tkinter as tk
from glob import glob

import pandas as pd

import answer_simplification_bars
import better_than_x
import lines
import rule_usage
import total_reductions
import utility


def gui():
    DIR = 'PostExam'
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

    graphs = ['answers', 'point plot', 'rule usage', 'lines', 'total reductions']
    row = 0
    column += 1
    for graph in graphs:
        var = tk.IntVar()
        if graph in ['point plot', 'total reductions']:
            var.set(0)
        else:
            var.set(1)
        tk.Checkbutton(master, text=graph, variable=var, bg=BACKGROUND, fg=FOREGROUND).grid(row=row, column=column)
        results[graph] = var
        row += 1

    tk.Button(master, text="Next", command=master.destroy, bg=BACKGROUND, fg=FOREGROUND).grid(row=row,
                                                                                              column=column)
    tk.Button(master, text="Exit", command=sys.exit, bg=BACKGROUND, fg=FOREGROUND).grid(row=row + 1,
                                                                                        column=column)
    master.mainloop()

    chosen_results = [csv_name for csv_name in results.keys() if '.csv' in csv_name and results[csv_name].get() == 1]

    if len(chosen_results) == 0:
        raise Exception('You did not choose any experiment')

    category = chosen_results[0].split('\\')[1]
    for index, result in enumerate(chosen_results):
        curr_category = result.split('\\')[1]
        if curr_category != category:
            raise Exception(f'Comparing across categories {category} and {curr_category}')
        chosen_results[index] = f'\\{DIR}\\{result}'

    comparison = {}
    if results['point plot'].get() == 1:
        if len(chosen_results) == 1:
            raise Exception('Must select more than 1 experiment if you want to make point plot')
        master = tk.Tk()
        master.configure(bg=BACKGROUND)
        master.title('Select result to use as comparison')
        row = 0
        for result in chosen_results:
            var = tk.IntVar()
            tk.Checkbutton(master, text=result, variable=var, bg=BACKGROUND, fg=FOREGROUND).grid(row=row)
            row += 1
            comparison[result] = var
        tk.Button(master, text="Choose", command=master.destroy, bg=BACKGROUND, fg=FOREGROUND).grid(row=max_row,
                                                                                                    column=column)
        tk.Button(master, text="Exit", command=sys.exit, bg=BACKGROUND, fg=FOREGROUND).grid(row=max_row + 1,
                                                                                            column=column)

        master.geometry("400x200")
        master.mainloop()

    comp = ''
    comparison_list = [comp for comp in comparison.keys() if comparison[comp].get() == 1]
    if len(comparison_list) > 1:
        raise Exception('Can only choose one experiment to compare against')
    elif results['point plot'].get() == 1:
        comp = comparison_list[0]

    print(f"Selected category: {category}")
    chosen_graphs = [graph for graph in results.keys() if not ('.csv' in graph) and results[graph].get() == 1]
    print(f"Selected graphs: {chosen_graphs}")
    return chosen_results, chosen_graphs, comp, category


def plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name, graphs, category):
    """
    Will create all plots from all graph functions in this directory, except the deprecated ones
    """
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    num_graphs = len(graphs)
    graphs_made = 0

    # Sanitise the data
    print("Sanitising the data")
    data_list = utility.sanitise_df_list(data_list)

    print("Making graphs")

    if 'answers' in graphs:
        answer_simplification_bars.plot(data_list, test_names, graph_dir + '\\best-experiment\\', category)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")

    if 'point plot' in graphs:
        for keep_largest_percent in [1, 0.1]:
            for how_much_better in [0.01, 0.025, 0]:
                better_than_x.plot(data_list, test_names,
                                   graph_dir + '\\best-experiment\\',
                                   experiment_to_compare_against_name, keep_largest_percent, how_much_better, category)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")

    if 'rule usage' in graphs:
        # Plots that has to do with application of rules
        rule_usage.plot(data_list, test_names, graph_dir + '\\rule-usage\\', category)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")

    if 'lines' in graphs:
        # metrics = ['verification time', 'verification memory', 'state space size', 'reduce time', 'reduced size', 'total time']
        metrics = ['verification time', 'state space size', 'reduce time', 'reduced size', 'total time']
        for metric in metrics:
            for percentage in [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]:
                for cutoff_time in [0, 0.5, 1, 5, 10, 30]:
                    lines.plot(data_list, test_names, graph_dir + '\\lines\\' + metric.replace(" ", "-") + '\\',
                               metric, percentage, cutoff_time, category)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")

    if 'total reductions' in graphs:
        total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\', category)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")


if __name__ == "__main__":
    tests, graphs, comparison, category = gui()

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, f'..\\graphs\\{category}\\')

    # Remove all graphs
    if os.path.isdir(graph_dir):
        shutil.rmtree(graph_dir)

    # Make new directories
    os.makedirs(graph_dir)
    os.makedirs(graph_dir + '\\rule-usage\\')
    os.makedirs(graph_dir + '\\reductions\\')
    os.makedirs(graph_dir + '\\best-experiment\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\verification-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\verification-memory\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\reduce-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\total-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\reduced-size\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\state-space-size\\')

    experiment_to_compare_against_name = os.path.split(os.path.splitext(comparison)[0])[1]
    # Directory for all our csv
    # csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    # csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]

    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, '..\\results')

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in tests]

    print(f"Selected graphs {test_names}")

    if not experiment_to_compare_against_name == '':
        print(f"Compared against {experiment_to_compare_against_name}")

    if experiment_to_compare_against_name == 'no-red':
        raise Exception('(all_graphs) Cannot use (no-red) as basis for comparison')

    data_list = [pd.read_csv(results_dir + csv, engine='python') for csv in tests]

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name, graphs, category)
