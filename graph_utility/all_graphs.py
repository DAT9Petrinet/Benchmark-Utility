import os
import sys
import shutil
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import answer_simplification_bars
import rule_usage_absolute
import rule_usage_percentage
import reduced_size
import time_memory_combined
import time_memory_lines
import reduction_points
import total_reductions
import time_size_ratios_lineplots
import time_size_avg_ratios
import rule_usage_absolute_models
import time_memory_points
import best_overall


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
    answer_simplification_bars.plot(data_list, test_names, graph_dir)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    best_overall.plot(data_list, test_names, graph_dir)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Plots that has to do with application of rules
    rule_usage_absolute.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    rule_usage_percentage.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    rule_usage_absolute_models.plot(data_list, test_names, graph_dir + '\\rule-usage\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Stuff to do with time and memory
    time_memory_combined.plot(data_list, test_names, graph_dir + '\\time-memory\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    metrics = ['time', 'memory']
    for metric in metrics:
        time_memory_lines.plot(data_list, test_names, graph_dir + '\\time-memory\\', metric)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_memory_points.plot(data_list, test_names, graph_dir + '\\time-memory\\', experiment_to_compare_against_name)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Stuff to do with reduction/size
    reduced_size.plot(data_list, test_names, graph_dir + '\\reductions\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    reduction_points.plot(data_list, test_names, graph_dir + '\\reductions\\', experiment_to_compare_against_name)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    total_reductions.plot(data_list, test_names, graph_dir + '\\reductions\\')
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Stuff to do with ratios
    time_size_ratios_lineplots.plot(data_list, test_names, graph_dir + '\\size-ratios\\',
                                    experiment_to_compare_against_name)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    time_size_avg_ratios.plot(data_list, test_names, graph_dir + '\\size-ratios\\', experiment_to_compare_against_name)
    times[graphs_made] = (round(time.time() * 1000) - time_when_started)
    graphs_made = graphs_made + 1
    print(f"{graphs_made}/{num_graphs} graphs made")

    # Print meme graph
    df = pd.DataFrame.from_dict(times, orient='index')
    print(df)
    plot = sns.lineplot(data=df)
    plot.set(
        title=f'Time spent making graphs',
        ylabel=f'time in ms',
        xlabel='number of models', yscale="log")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

    plt.savefig(graph_dir + 'time_spent_making_graphs', bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    # Results used for comparisons
    if len(sys.argv) == 1:
        experiment_to_compare_against_name = 'base-rules'
    else:
        experiment_to_compare_against_name = sys.argv[1]
        if experiment_to_compare_against_name == 'no-red':
            raise Exception('(all_graphs) Cannot use no-red as basis for comparison, as this has no reductions')

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
    os.makedirs(graph_dir + '\\time-memory\\')

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '..\\saved\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot_all(data_list, test_names, graph_dir, experiment_to_compare_against_name)
