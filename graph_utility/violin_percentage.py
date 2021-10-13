import matplotlib.pyplot as plt
import seaborn as sns
import copy


def plot(data_list, test_names, rules, graph_dir):
    data_list = copy.deepcopy(data_list)
    test_names = copy.deepcopy(test_names)
    # Produce one plot (png) for each csv
    for index, data in enumerate(data_list):
        if "no-red" in test_names[index]:
            continue
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group the data by each model, and sum the number of times each rule has been applied by each model
        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')

        # Make the data into true or false values instead, to signify if a rule has been used in the model
        # instead of how many times
        percentages = ((data_grouped_by_model > 0) * 1) * 100

        # Plot the plot
        sns.set_theme(style="darkgrid", palette="pastel")
        plot = sns.violinplot(data=percentages, bw=0.1)
        plot.set(title=f'({test_names[index]}) chance for a rule to be used in a model', ylabel='Chance to be used')
        plt.savefig(graph_dir + f'{test_names[index]}_rule_violin_percentage.png')
        plt.clf()
