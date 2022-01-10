import copy
import re
import warnings

import matplotlib.pyplot as plt
import seaborn as sns

import utility

warnings.filterwarnings("error")


def plot(data_list, test_names, graph_dir, category):
    # The deepcopies are because in the 'all_graphs' the data_list are used for all plots,
    # so each function will make their own copy
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)

    data_list, test_names = utility.remove_no_red(data_list, test_names)

    data_list = utility.remove_rows_with_no_answers_or_query_simplification(data_list)

    # Make one plot (png) for each csv
    for test_index, data in enumerate(data_list):

        # Find rule names
        rules = [column for column in data.columns.tolist() if
                 "rule" in column]

        # Sum over all rows the number of times each rule has been used
        rules_summed = data[rules].agg('sum').to_frame().T

        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')
        percentages = (((((data_grouped_by_model > 0) * 1).mean()) * 100).to_frame()).T
        models_using_rule = ((data_grouped_by_model > 0) * 1).agg('sum').to_frame().T

        new_test_name = utility.rename_test_name_for_paper_presentation(test_names)[test_names[test_index]]

        # Remove the 'Rule' part of e.g 'Rule A'
        for df in [rules_summed, percentages, models_using_rule]:
            df.rename(columns=lambda x: re.sub('rule', '', x), inplace=True)

        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.barplot(data=rules_summed)
        try:
            plot.set_yscale("log")
        except:
            print(f"Test has probably gone wrong, had no application of any rules: {test_names[test_index]}")
            plot.set_yscale("linear")
        plot.set(title=f'{new_test_name} number of times rules are used', ylabel='uses', xlabel='rules')
        # This for-loop puts the number of times each rule has been used, on top of the bar
        for p in plot.patches:
            plot.annotate(format(p.get_height().astype(int), 'd'),
                          ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                          ha='center', va='center',
                          size=12,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(graph_dir + f'{category}_{test_names[test_index]}_rule_usage_absolute.svg', dpi=600, format="svg")
        plt.clf()

        # Plot the plot
        plot = sns.barplot(data=percentages)
        plot.set(title=f'{new_test_name} percentage of models using rules', ylabel='uses in %',
                 xlabel='rules')
        # Plots numbers above bars
        for p in plot.patches:
            if p.get_height() != 0.0:
                plot.annotate(format(p.get_height(), '.1f'),
                              (p.get_x() + p.get_width() / 2.,
                               p.get_height()),
                              ha='center', va='center',
                              size=12,
                              xytext=(0, 8),
                              textcoords='offset points')
        plt.savefig(graph_dir + f'{category}_{test_names[test_index]}_rule_usage_percentage.svg', dpi=600, format="svg")
        plt.clf()

        # Plot the plot
        plot = sns.barplot(data=models_using_rule)
        plot.set(title=f'{new_test_name} number of models using rules', ylabel='uses', xlabel='rules')
        # Plots numbers above bars
        for p in plot.patches:
            if p.get_height() != 0:
                plot.annotate(format(p.get_height().astype(int), 'd'),
                              ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                              ha='center', va='center',
                              size=12,
                              xytext=(0, 8),
                              textcoords='offset points')
        plt.savefig(graph_dir + f'{category}_{test_names[test_index]}_rule_usage_absolute_models.svg', dpi=600, format="svg")
        plt.close()
