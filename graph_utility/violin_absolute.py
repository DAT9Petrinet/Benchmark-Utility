import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import copy


def plot(data_list, test_names, graph_dir):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)
    # Produce one plot (png) for each csv
    for index, data in enumerate(data_list):
        if "no-red" in test_names[index]:
            continue

        rules = [column for column in data.columns.tolist() if
                 "rule" in column]
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group the data by each model, and sum the number of times each rule has been applied by each model
        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')

        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.violinplot(data=data_grouped_by_model, bw=0.1)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) rule usage per model', ylabel='uses')
        plt.savefig(graph_dir + f'{test_names[index]}_rule_violin_absolute.png')
        plt.clf()

if __name__ == "__main__":
    # Find the directory to save figures
    script_dir = os.path.dirname(__file__)
    graph_dir = os.path.join(script_dir, '..\graphs\\')

    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    paths = sys.argv[1:]
    test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

    data_list = [pd.read_csv(path) for path in paths]
    plot(data_list, test_names, graph_dir)
