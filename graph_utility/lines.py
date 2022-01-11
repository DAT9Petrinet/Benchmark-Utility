import copy
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import utility


def plot(data_list, test_names, graph_dir, metric, keep_largest_percent, cutoff_time, category):
    linestyles = [
        [1, 1],
        [2, 2, 10, 2],
        [5, 5],
        [6, 2],
        [3, 1],
        [3, 1, 3, 1, 1, 1],
        [3, 1, 1, 1],
        [3, 5, 1, 5, 1, 5],
        [1, 1, 3, 1, 6, 1],
        [3, 1, 1, 1, 1, 1]]

    base_width = 3
    other_width = 1.5
    base_name = 'base'
    cutoff_times = {'total time': cutoff_time, 'verification time': cutoff_time, 'reduce time': cutoff_time}

    time_metrics = ['total time', 'verification time', 'reduce time']

    if metric == "verification memory":
        return

    if metric in time_metrics and os.path.isfile(
            graph_dir + f'{category}_{metric.replace(" ", "_")}_above_{cutoff_times[metric]}_seconds.svg'):
        return
    elif os.path.isfile(graph_dir + f'{category}_{metric.replace(" ", "_")}_top_{keep_largest_percent * 100}.svg'):
        return

    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    # Dataframe to hold data from all csvs
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        data = utility.remove_errors_df(data)

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

        if metric in time_metrics:
            metric_data = metric_data[metric_data[metric] >= cutoff_times[metric]]
        else:
            n = int(metric_data.shape[0] * keep_largest_percent)
            metric_data = metric_data.tail(n)

        # Rename the column to include the name of the test
        metric_data.rename(columns={f'{metric}': test_names[index]}, inplace=True)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = metric_data
            continue
        combined_df = pd.concat([combined_df, metric_data], axis=1)

    combined_df.rename(utility.rename_test_name_for_paper_presentation(test_names), axis='columns', inplace=True)

    sns.set_theme(style="darkgrid")
    custom_palette = {}
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


    my_dashes = linestyles[0:len(combined_df.columns) - 1]

    columns_without_base = [column for column in combined_df.columns if column != base_name]
    # sns.set(rc={'figure.figsize': (11.7, 8.27)})
    if not (len(combined_df) == 0 or len(combined_df.columns) == 0):
        # Plot the plot
        #
        if base_name in test_names:
            sns.lineplot(data=combined_df[base_name], palette=custom_palette, linewidth=base_width)
            plot = sns.lineplot(data=combined_df[columns_without_base], palette=custom_palette, linewidth=other_width,
                                dashes=my_dashes)
        else:
            plot = sns.lineplot(data=combined_df, palette=custom_palette)
        plot.set(
            ylabel=f'{unit}',
            xlabel='queries')

        #if metric in time_metrics:
        #    plot.set(title=f'{metric} per test instance sorted, above {cutoff_time[metric]} seconds')
        #else:
        #    plot.set(title=f'{metric} per test instance sorted, using {keep_largest_percent * 100}% largest tests')

        if metric == "reduced size":
            plot.set(yscale="linear")
            plt.ylim(0, 125)
        #elif metric in ["state space size", 'verification memory']:
        #    plot.set(yscale="log")
        else:
            plot.set(yscale="linear")
        # plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)
        plt.legend(loc='upper left', borderaxespad=0)

        if metric in time_metrics:
            plt.savefig(graph_dir + f'{category}_{metric.replace(" ", "_")}_above_{cutoff_times[metric]}_seconds.svg',
                        bbox_inches='tight', dpi=600, format="svg")
        else:
            plt.savefig(graph_dir + f'{category}_{metric.replace(" ", "_")}_top_{keep_largest_percent * 100}.svg',
                        bbox_inches='tight', dpi=600, format="svg")
        plt.close()
