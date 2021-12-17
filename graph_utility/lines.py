import copy

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def plot(data_list, test_names, graph_dir, metric, keep_largest_percent):
    """
    Can be called with a column name, and will plot all values from this column sorted as a line.
    Can be called with multiple csvs, and will plot all lines on same graph
    """

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Dataframe to hold data from all csvs
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        data = utility.remove_errors_df(data)

        # Get data from relevant column sorted
        n = int(data.shape[0] * keep_largest_percent)

        res_df = pd.DataFrame()
        if metric in ['verification time', 'verification memory']:
            res_df[metric] = data[data['answer'] != 'NONE'][metric]
        elif metric == 'reduced size':
            res_df[metric] = data.apply(
                utility.get_reduced_size,
                axis=1)
        elif metric == 'total time':
            res_df[metric] = data[data['answer'] != 'NONE'].apply(
                utility.get_total_time,
                axis=1)
        elif metric == 'state space size':
            res_df = data.drop(data.index[data['state space size'] == 0])
        # Reduce time
        else:
            res_df[metric] = data[metric]

        res_df.dropna(subset=[metric], inplace=True)
        # Sort
        # For reduced size, we must sort the other way
        if metric == 'reduced size':
            metric_data = ((res_df[f'{metric}'].sort_values(ascending=True)).reset_index()).drop(columns=
                                                                                                 'index')
        else:
            metric_data = ((res_df[f'{metric}'].sort_values()).reset_index()).drop(columns=
                                                                                   'index')

        metric_data = metric_data.tail(n)

        # Rename the column to include the name of the test
        metric_data.rename(columns={f'{metric}': test_names[index]}, inplace=True)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = metric_data
            continue
        combined_df = pd.concat([combined_df, metric_data], axis=1)

    sns.set_theme(style="darkgrid")
    custom_palette = {}

    # dashes = []
    for column_index, column in enumerate(combined_df.columns):
        custom_palette[column] = utility.color((column_index + 1) / len(combined_df.columns))

    if metric in ["verification time", 'reduce time', 'total time']:
        unit = 'seconds'
    elif metric == 'verification memory':
        unit = 'kB'
    elif metric == 'state space size':
        unit = 'number of states'
    elif metric == 'reduced size':
        unit = 'ratio given by post size/pre size'

    sns.set(rc={'figure.figsize': (11.7, 8.27)})
    if not (len(combined_df) == 0 or len(combined_df.columns) == 0):
        # Plot the plot
        plot = sns.lineplot(data=combined_df, palette=custom_palette, dashes=[(1, 0)] * len(combined_df.columns))
        plot.set(
            title=f'{metric} per test instance sorted, using {keep_largest_percent * 100}% largest tests',
            ylabel=f'{unit}',
            xlabel='test instances')
        if metric == "reduced size":
            plot.set(yscale="linear")
            plt.ylim(0, 125)
        else:
            plot.set(yscale="log")
        #plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.legend(loc='upper left', borderaxespad=0)



        plt.savefig(graph_dir + f'{metric.replace(" ", "_")}_top_{keep_largest_percent * 100}%.png',
                    bbox_inches='tight')
        plt.clf()
