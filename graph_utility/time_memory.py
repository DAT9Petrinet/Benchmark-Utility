import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir, metric):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)
    # Dataframe to hold data from all csv's
    # Rows will be models
    # Columns are (test_name)-time and (test_name)-memory
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(
            data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group by model name, and sum over metric, sort so lowest metric first
        metric_data = ((data[f'{metric}'].sort_values()).reset_index()).drop(columns=
                                                                          'index')
        # Rename the column to include the name of the test
        metric_data.rename(columns={f'{metric}': f"{test_names[index]}-{metric}"}, inplace=True)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = metric_data
            continue
        combined_df = combined_df.join(metric_data)


    # Plot the plot
    plot = sns.lineplot(data=combined_df)
    plot.set(
        title=f'model checking {metric} per test instance',
        ylabel='kB',
        xlabel='test instances', yscale="log")
    plt.legend(bbox_to_anchor=(1.02, 1), loc='best', borderaxespad=0)

    plt.savefig(graph_dir + f'{metric}_per_model.png', bbox_inches='tight')
    plt.clf()


if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    data_list = [pd.read_csv(path) for path in paths]
    metrics = ['time', 'memory']
    for metric in metrics:
        plot(data_list, test_names, graph_dir, metric)