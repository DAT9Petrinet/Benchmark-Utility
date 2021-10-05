import matplotlib.pyplot as plt
import seaborn as sns


def plot(data_list, test_names, rules):
    sns.set_theme(style="whitegrid", palette="pastel")

    # Produce one plot (png) for each csv
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group the data by each model, and sum the number of times each rule has been applied by each model
        data_grouped_by_model = data.groupby(['model name'])[rules].agg('sum')

        # Plot the plot
        plot = sns.violinplot(data=data_grouped_by_model, bw=0.1)
        plot.set_yscale("log")
        plot.set(title=f'({test_names[index]}) rule usage per model', ylabel='uses')
        plt.savefig(f'../graphs/{test_names[index]}_rule_violin_absolute.png')
        plt.clf()
