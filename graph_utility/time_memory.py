import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import re


def plot(data_list, test_names):
    # Dataframe to hold data from all csv's
    # Rows will be models
    # Columns are (test_name)-time and (test_name)-memory
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(
            data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group by model name, and sum over time, sort so lowest time first
        time_data = ((data['time'].sort_values()).reset_index()).drop(columns=
                                                                      'index')
        # Rename the column to include the name of the test
        time_data.rename(columns={'time': f"{test_names[index]}-time"}, inplace=True)

        # Group by model name, and sum over memory, sort so lowest memory first
        memory_data = ((data['memory'].sort_values()).reset_index()).drop(columns=
                                                                          'index')
        # Rename the column to include the name of the test
        memory_data.rename(columns={'memory': f"{test_names[index]}-memory"}, inplace=True)

        # Join the time and memory dataframes
        memory_time_data = time_data.join(memory_data)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = memory_time_data
            continue
        combined_df = combined_df.join(memory_time_data)

    # Recolor lines and choose dashes
    regex = r"(.*)-(time|memory)$"
    sns.set_theme(style="darkgrid", palette="pastel")
    pal = sns.color_palette()
    custom_palette = {}
    dashes = []
    for column_index, column in enumerate(combined_df.columns):
        matches = re.finditer(regex, column, re.MULTILINE)
        for match in matches:
            data_type = match.groups()[1]
            if data_type == "time":
                dashes.append((1, 0))
            elif data_type == "memory":
                dashes.append((2, 2))
            else:
                raise Exception("(time_memory) Should not be able to reach this")
            test_name = match.groups()[0]
            custom_palette[column] = pal[test_names.index(test_name)]

    # Plot the plot
    plot = sns.lineplot(data=combined_df, linewidth=2.5, palette=custom_palette,
                        dashes=dashes)
    plot.set(
        title=f'model checking time and memory per model',
        ylabel='seconds or kB',
        xlabel='models', yscale="log")
    plt.legend(bbox_to_anchor=(1.02, 0.55), loc='best', borderaxespad=0)

    plt.savefig('../graphs/time-memory_per_model.png', bbox_inches='tight')
    plt.clf()
