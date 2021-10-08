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

        # Group the data by each model, and sum the number of times each rule has been applied by each model
        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')

        # Get the percentage of model that has applied a rule
        percentages = (((((data_grouped_by_model > 0) * 1).mean()) * 100).to_frame()).T

        percentages.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.barplot(data=percentages)
        plot.set(title=f'({test_names[index]}) percentage of models using rules', ylabel='uses in \%')
        # Plots numbers above bars
        for p in plot.patches:
            plot.annotate(format(p.get_height(), '.1f'),
                          (p.get_x() + p.get_width() / 2., p.get_height()),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(graph_dir + f'{test_names[index]}_rule_usage_percentage.png')
        plt.clf()
