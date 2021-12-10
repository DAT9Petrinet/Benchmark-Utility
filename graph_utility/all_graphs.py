import os
import shutil
from pathlib import Path
from tkinter import filedialog
import sys
import pandas as pd

import answer_simplification_bars
import better_than_x
import rule_usage
import time_memory_lines
import total_reductions
import utility


def plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    """
    Will create all plots from all graph functions in this directory, except the deprecated ones
    """
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    graphs = [filename for filename in os.listdir(os.path.dirname(__file__)) if
              '.py' in filename and filename not in ['all_graphs.py', 'jable.py', 'utility.py']]
    num_graphs = len(graphs)
    graphs_made = 0

    # Sanitise the data
    print("Sanitising the data")
    data_list = utility.sanitise_df_list(data_list)

    print("Making graphs")
    # General graphs not fitting totally into the next categories
    answer_simplification_bars.plot(data_list, test_names, graph_dir + '\\best-experiment\\')
    graphs_made += 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    for keep_largest_percent in [1, 0.1]:
        for how_much_better in [0.01, 0.025, 0]:
            better_than_x.plot(data_list, test_names,
                               graph_dir + '\\best-experiment\\',
                               experiment_to_compare_against_name, keep_largest_percent, how_much_better)
    graphs_made += 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Plots that has to do with application of rules
    rule_usage.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    graphs_made += 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    metrics = ['verification time', 'verification memory', 'state space size', 'reduce time', 'reduced size',
               'total time']
    for metric in metrics:
        for percentage in [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]:
            time_memory_lines.plot(data_list, test_names, graph_dir + '\\lines\\' + metric.replace(" ", "-") + '\\',
                                   metric, percentage)
    graphs_made += 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\')
    graphs_made += 1
    print(f"{graphs_made}/{num_graphs} graphs made")


if __name__ == "__main__":

    # Results used for comparisons
    '''if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]
        if experiment_to_compare_against_name == 'no-red':
            raise Exception('(all_graphs) Cannot use (no-red) as basis for comparison')'''

    #print(f'(all_graphs) using ({experiment_to_compare_against_name}) for comparison')

    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

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

    tf = filedialog.askopenfilenames(
        initialdir=Path(script_dir).parent.joinpath('saved'),
        title="Select experiments",
        filetypes=(("Text Files", "*.csv"),)
    )

    if len(tf) == 0:
        raise Exception('You did not choose any files')

    # Directory for all our csv
    #csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    #csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in tf]

    print(f"You selected following files: {test_names} \n Which do you want to use as basis for comparison? \n Press Enter for default (base-rules)")
    experiment_to_compare_against_name = input()
    if len(experiment_to_compare_against_name) == 0:
        experiment_to_compare_against_name = 'base-rules'
    elif experiment_to_compare_against_name == 'no-red':
        raise Exception('(all_graphs) Cannot use (no-red) as basis for comparison')
    elif experiment_to_compare_against_name not in test_names:
        raise Exception(f'{experiment_to_compare_against_name} not found in the experiments that you chose')

    data_list = [pd.read_csv(csv, engine='python') for csv in tf]

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name)
