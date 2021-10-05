import matplotlib.pyplot as plt
import seaborn as sns


def plot(data_list, test_names, rules):
    sns.set_style("whitegrid")

    for index, data in enumerate(data_list):
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
        grouped_data = data.groupby(['model name'])[rules].agg('sum')

        plot = sns.violinplot(data=grouped_data)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) rule usage per model', ylabel='uses')
        for p in plot.patches:
            plot.annotate(format(p.get_height(), '.1f'),
                          (p.get_x() + p.get_width() / 2, p.get_height()),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(f'../graphs/{test_names[index]}_rule_violin_absolute.png')
        plt.clf()
