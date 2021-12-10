import os
import shutil
import sys
import time
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

import answer_simplification_bars
import best_overall
import reduced_size
import reduction_points
import rule_usage_absolute
import rule_usage_absolute_models
import rule_usage_percentage
import time_memory_combined
import time_memory_lines
import time_memory_points
import time_size_avg_ratios
import time_size_ratios_lineplots
import total_reductions


def plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name):
    """
    Will create all plots from all graph functions in this directory, except the deprecated ones
    """
    # Get number of files in this directory, remove the ones we do not use
    # Can use this for the prints
    graphs = [filename for filename in os.listdir(os.path.dirname(__file__)) if
              '.py' in filename and filename != 'all_graphs.py']
    num_graphs = len(graphs)
    graphs_made = 0

    times = dict()
    time_when_started = time.time()
    # General graphs not fitting totally into the next categories
    answer_simplification_bars.plot(data_list, test_names, graph_dir + '\\best-experiment\\')
    times['answer/simplification bars'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    best_overall.plot(data_list, test_names, graph_dir + '\\best-experiment\\')
    times['best experiment overall'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    # Plots that has to do with application of rules
    rule_usage_absolute.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times['rule usage absolute'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    rule_usage_percentage.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times['models using rule percentage'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    rule_usage_absolute_models.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times['models using rule absolute'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    # Stuff to do with time and memory
    time_memory_combined.plot(data_list, test_names, graph_dir + '\\time-memory-size\\')
    times['time/memory lines combined'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    metrics = ['verification time', 'verification memory', 'state space size']
    for metric in metrics:
        time_memory_lines.plot(data_list, test_names, graph_dir + '\\time-memory-size\\', metric)
    times['time/memory lines'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    time_memory_points.plot(data_list, test_names, graph_dir + '\\time-memory-size\\', experiment_to_compare_against_name)
    times['time/memory points'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    # Stuff to do with reduction/size
    reduced_size.plot(data_list, test_names, graph_dir + '\\reductions\\')
    times['reduced size'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    reduction_points.plot(data_list, test_names, graph_dir + '\\reductions\\', experiment_to_compare_against_name)
    times['reduction points'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\')
    times['total reductions'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    # Stuff to do with ratios
    time_size_ratios_lineplots.plot(data_list, test_names, graph_dir + '\\size-ratios\\',
                                    experiment_to_compare_against_name)
    times['ratios lineplots'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_when_started = time.time()
    time_size_avg_ratios.plot(data_list, test_names, graph_dir + '\\size-ratios\\', experiment_to_compare_against_name)
    times['avg ratios'] = (round(time.time()) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

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
        if width < (max_width / 3):
            left += 1
            width *= 2
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
    os.makedirs(graph_dir + '\\size-ratios\\')
    os.makedirs(graph_dir + '\\reductions\\')
    os.makedirs(graph_dir + '\\time-memory-size\\')
    os.makedirs(graph_dir + '\\best-experiment\\')

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '../results\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv, engine='python') for csv in csvs]

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name)
