import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# The first csv will be used as numerator in the plots
def plot(data_list, test_names, unneeded_columns):
    sns.set_theme(style="whitegrid", palette="pastel")

    # Find indices to remove
    # Cannot simply remove them per csv, we have to go through all csvs first, and
    # find any rows that has been solved by simplification, or has 'NONE' answers, as they should be removed from all csv
    rows_to_delete = None
    for df in data_list:
        index = df.index

        # Find all indices where the query has been solved by simplification
        condition_simplification = df['solved by query simplification']
        simplification_indices = index[condition_simplification]
        simplification_indices_set = set(simplification_indices.tolist())

        # Find all rows where we have 'NONE' answer
        condition_answer = df['answer'] == 'NONE'
        answer_indices = index[condition_answer]
        answer_indices_set = set(answer_indices.tolist())

        # Take the union, (note sets, so we don't have duplicates)
        combined_indices = list(answer_indices_set.union(simplification_indices_set))
        rows_to_delete = df.index[combined_indices]

    # Remove the rows, columns not needed, and group the data based on models
    for index, data in enumerate(data_list):
        data.drop(rows_to_delete, inplace=True)
        data.drop(columns=unneeded_columns, inplace=True)
        data_list[index] = (data.groupby(['model name']).agg('mean')).reset_index()

    # Get sizes from the data that will be used as numerator
    num_rows = len(data_list[0])
    pre_sizes_numerator = [] * num_rows
    post_sizes_numerator = [] * num_rows
    for index, row in data_list[0].iterrows():
        pre_sizes_numerator.append(int(row['prev place count'] + row['prev transition count']))
        post_sizes_numerator.append(int(row['post place count'] + row['post transition count']))

    # Dataframe to hold the size rato between reduced nets
    size_ratios = pd.DataFrame()

    # Go through all other csv and calculate the ratios
    for test_index, data in enumerate(data_list[1:]):
        df = pd.DataFrame()
        ratios = [] * num_rows
        # Iterate through all rows and compute ratio
        # All this with lists and stuff, and this iteration should probaly be handled better using pandas, but works :shrug
        for index, row in data.iterrows():
            size_pre_reductions = int(row['prev place count'] + row['prev transition count'])

            # Sanity check
            if pre_sizes_numerator[index] != size_pre_reductions:
                raise Exception("Not comparing same rows")

            size_post_reduction = int(row['post place count'] + row['post transition count'])
            ratio = post_sizes_numerator[index] / size_post_reduction
            ratios.append(ratio)

        # Add ratios to the current dataframe, with the tests being compared as the column name
        df[f"{test_names[0]}/{test_names[test_index + 1]}"] = ratios

        # Add ratios from this comparison to size_ratios
        if test_index == 0:
            size_ratios = df
        else:
            size_ratios.append(df)

    # plot the plot
    sns.lineplot(data=size_ratios).set(xlabel='models', ylabel='size ratio', yscale="linear",
                                       title='Reduced size of nets')
    plt.savefig('../graphs/reduced_size_compared.png')
    plt.clf()
