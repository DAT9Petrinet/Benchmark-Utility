import matplotlib.pyplot as plt
import seaborn as sns


def plot(data_list, test_names, rules):
    sns.set_style("whitegrid")

    for index, data in enumerate(data_list):
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
        data_summed = data[rules].agg('sum').to_frame().T

        plot = sns.barplot(data=data_summed)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) number of times rules are used', ylabel='uses')
        for p in plot.patches:
            plot.annotate(format(p.get_height().astype(int), 'd'),
                          ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(f'../graphs/{test_names[index]}_rule_usage_absolute.png')
        plt.clf()
