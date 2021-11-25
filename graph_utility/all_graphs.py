import os
import shutil
import sys
import time

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import answer_simplification_bars
import best_overall
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
    times = dict()
    time_when_started = time.time()

    def update_globals(experiment_name, graphs_made):
        times[experiment_name] = (round(time.time()) - time_when_started)
        graphs_made += 1
        print(f"{graphs_made}/{num_graphs} graphs made")
        return graphs_made

    # Sanitise the data
    data_list = utility.sanitise_df_list(data_list)

    # General graphs not fitting totally into the next categories
    time_when_started = time.time()
    answer_simplification_bars.plot(data_list, test_names, graph_dir + '\\best-experiment\\')
    graphs_made = update_globals('answer/simplification bars', graphs_made)

    '''time_when_started = time.time()
    for keep_largest_percent in [0.1]:
        for how_much_better in [0.025]:
            best_overall.plot(data_list, test_names, graph_dir + '\\best-experiment\\' + '\\best-overall\\',
                              keep_largest_percent,
                              how_much_better)
    graphs_made = update_globals('best experiment overall', graphs_made)

    time_when_started = time.time()
    for keep_largest_percent in [0.25, 0.1]:
        better_than_x.plot(data_list, test_names,
                           graph_dir + '\\best-experiment\\' + f'\\compared-to-{experiment_to_compare_against_name}\\',
                           experiment_to_compare_against_name, keep_largest_percent)
    graphs_made = update_globals('best experiment overall', graphs_made)'''

    time_when_started = time.time()
    # Plots that has to do with application of rules
    rule_usage.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    graphs_made = update_globals('rule usages', graphs_made)

    time_when_started = time.time()
    metrics = ['verification time', 'verification memory', 'state space size', 'reduce time', 'reduced size',
               'total time']
    for metric in metrics:
        for percentage in [0.01, 0.025, 0.05, 0.1, 0.5, 1]:
            time_memory_lines.plot(data_list, test_names, graph_dir + '\\lines\\' + metric.replace(" ", "-") + '\\',
                                   metric, percentage)
    graphs_made = update_globals('time/memory lines', graphs_made)

    time_when_started = time.time()
    total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\')
    graphs_made = update_globals('total reductions', graphs_made)

    # Print meme graph
    df = pd.DataFrame.from_dict(times, orient='index')
    # Plot the plot
    sns.set_theme(style="darkgrid", palette="pastel")
    plot = df.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10), legend=False)
    plt.xscale('linear')
    plt.xlabel("seconds")
    plt.ylabel('graphs')
    plt.title('Time in seconds spent making graphs')

    # Find max width, in order to move the very small numbers away from the bars
    max_width = 0
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        max_width = max(width, max_width)
    # Plot the numbers in the bars
    for p in plot.patches:
        left, bottom, width, height = p.get_bbox().bounds
        plot.annotate(int(width), xy=(left + width / 2, bottom + height / 2),
                      ha='center', va='center')

    plt.savefig(graph_dir + f'time_spent_making_graphs.png', bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    # Results used for comparisons
    if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]
        if experiment_to_compare_against_name == 'no-red':
            raise Exception('(all_graphs) Cannot use (no-red) as basis for comparison, as this has no reductions')

    print(f'(all_graphs) using ({experiment_to_compare_against_name}) for basis for all comparisons')
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
    os.makedirs(graph_dir + '\\best-experiment\\' + '\\best-overall\\')
    os.makedirs(graph_dir + '\\best-experiment\\' + f'\\compared-to-{experiment_to_compare_against_name}\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\verification-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\verification-memory\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\reduce-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\total-time\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\reduced-size\\')
    os.makedirs(graph_dir + '\\lines\\' + '\\state-space-size\\')

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv, engine='python') for csv in csvs]

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name)
