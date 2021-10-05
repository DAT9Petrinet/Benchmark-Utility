import matplotlib.pyplot as plt
import seaborn as sns


def plot(data_list, test_names, rules):
    sns.set_theme(style="whitegrid", palette="pastel")

    # Make one plot (png) for each csv
    for index, data in enumerate(data_list):
        if "no-red" in test_names[index]:
            continue

        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Sum over all rows the number of times each rule has been used
        rules_summed = data[rules].agg('sum').to_frame().T

        plot = sns.barplot(data=rules_summed)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) number of times rules are used', ylabel='uses')
        # This for loop puts the number of times each rule has been used, on top of the bar
        for p in plot.patches:
            plot.annotate(format(p.get_height().astype(int), 'd'),
                          ((p.get_x() + p.get_width() / 2).astype(int), p.get_height().astype(int)),
                          ha='center', va='center',
                          size=10,
                          xytext=(0, 8),
                          textcoords='offset points')
        plt.savefig(f'../graphs/{test_names[index]}_rule_usage_absolute.png')
        plt.clf()
