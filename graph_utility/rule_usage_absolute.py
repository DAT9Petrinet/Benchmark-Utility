import re

import matplotlib.pyplot as plt
import seaborn as sns


def plot(data_list, test_names, rules, graph_dir):
    # Make one plot (png) for each csv
    for index, data in enumerate(data_list):
        if "no-red" in test_names[index]:
            continue

        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Sum over all rows the number of times each rule has been used
        rules_summed = data[rules].agg('sum').to_frame().T

        rules_summed.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)

        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.barplot(data=rules_summed)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) number of times rules are used', ylabel='uses', xlabel='rules')
        # This for loop puts the number of times each rule has been used, on top of the bar
        for p in plot.patches:
            plot.annotate(format(p.get_height().astype(int), 'd'),
                          ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(graph_dir + f'{test_names[index]}_rule_usage_absolute.png')
        plt.clf()
