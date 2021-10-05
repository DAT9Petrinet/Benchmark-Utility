import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Takes a number of csv as input
# The first csv will be used as numerator in the plots


def plot(data_list, test_names, unneeded_columns):
    sns.set_style("whitegrid")
    size_ratios = pd.DataFrame()
    # Find indices to remove
    rows_to_delete = None
    for df in data_list:
        index = df.index

        condition_simplification = df['solved by query simplification']
        simplification_indices = index[condition_simplification]
        simplification_indices_set = set(simplification_indices.tolist())

        condition_answer = df['answer'] == 'NONE'
        answer_indices = index[condition_answer]
        answer_indices_set = set(answer_indices.tolist())

        combined_indices = list(answer_indices_set.union(simplification_indices_set))
        rows_to_delete = df.index[combined_indices]

    for df in data_list:
        df = df.drop(rows_to_delete, inplace=True)

    for index, df in enumerate(data_list):
        df.drop(unneeded_columns, axis=1, inplace=True)
        data_list[index] = (df.groupby(['model name']).agg('mean')).reset_index()

    num_rows = len(data_list[0])
    pre_sizes_numerator = [] * num_rows
    post_sizes_numerator = [] * num_rows
    for index, row in data_list[0].iterrows():
        pre_sizes_numerator.append(int(row['prev place count'] + row['prev transition count']))
        post_sizes_numerator.append(int(row['post place count'] + row['post transition count']))

    for test_index, data in enumerate(data_list[1:]):
        df = pd.DataFrame()
        ratios = [] * num_rows
        for index, row in data.iterrows():
            size_pre_reductions = int(row['prev place count'] + row['prev transition count'])

            if pre_sizes_numerator[index] != size_pre_reductions:
                raise Exception("Not comparing same rows")

            size_post_reductions = int(row['post place count'] + row['post transition count'])
            ratio = post_sizes_numerator[index] / size_post_reductions
            ratios.append(ratio)

        df[f"{test_names[0]}/{test_names[test_index + 1]}"] = ratios
        if test_index == 0:
            size_ratios = df
        else:
            size_ratios.append(df)

    sns.lineplot(data=size_ratios).set(xlabel='models', ylabel='size ratio', yscale="linear",
                                       title='Reduced size of nets')
    plt.savefig('../graphs/reduced_size_compared.png')
    plt.clf()
