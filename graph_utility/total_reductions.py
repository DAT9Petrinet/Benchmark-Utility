import copy
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def plot(data_list, test_names, graph_dir):
    """
        Plots 3 bars for each experiment, one for how many transitions, places and both has been reduced
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Remove test with no reductions
    data_list, test_names = utility.remove_no_red(data_list, test_names)

    # List to hold the reductions for each experiment
    total_reductions = []
    transitions_reductions = []
    places_reductions = []
    # Go through each experiment
    for test_index, data in enumerate(data_list):
        transition_reduction_sum = data['prev transition count'].sum() - data['post transition count'].sum()
        place_reduction_sum = data['prev place count'].sum() - data['post place count'].sum()

        total_reductions.append(place_reduction_sum + transition_reduction_sum)
        transitions_reductions.append(transition_reduction_sum)
        places_reductions.append(place_reduction_sum)

    # Create dataframe
    points_df = pd.DataFrame(
        {'total': total_reductions, 'places': places_reductions, 'transitions': transitions_reductions})

    # Rename indices to be test names, instead of int index
    points_df = utility.rename_index_to_test_name(points_df, test_names)

    data_to_plot = utility.split_into_all_with_without(points_df)
    png_names = ['all', 'with', 'without']

    for index, data in enumerate(data_to_plot):
        if index > 0:
            continue
        if len(data) == 0 or len(data.columns) == 0:
            continue
        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = data.plot(kind='barh', width=0.75, linewidth=2, figsize=(10, 10))

        plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.xscale('log')
        plt.xlabel("reductions")
        plt.ylabel('experiments')

        # Plot the numbers in the bars
        for p in plot.patches:
            left, bottom, width, height = p.get_bbox().bounds
            plot.annotate(int(width), xy=(left + width, bottom + height / 2),
                          ha='center', va='center')

        plt.savefig(graph_dir + f'total_reductions_{png_names[index]}.png', bbox_inches='tight')
        plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\' + '\\reductions\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    # Directory for all our csv
    csv_dir = os.path.join(script_dir, '../results\\')

    # Read csv data
    csvs = [file for file in os.listdir(csv_dir) if
            '.csv' in file]

    # Find names of the tests, to be used in graphs and file names
    test_names = [os.path.split(os.path.splitext(csv)[0])[1] for csv in csvs]

    data_list = [pd.read_csv(csv_dir + csv) for csv in csvs]

    plot(data_list, test_names, graph_dir)
