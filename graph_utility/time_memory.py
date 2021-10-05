import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names):
    sns.set_theme(style="whitegrid", palette="pastel")

    # Dataframe to hold data from all csv's
    # Rows will be models
    # Columns are (test_name)-time and (test_name)-memory
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        # Remove rows where query simplification has been used, or where there isn't an answer
        data = data.drop(
            data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)

        # Group by model name, and sum over time, sort so lowest time first
        time_data = (((data.groupby(['model name'])['time'].agg('sum')).sort_values()).reset_index()).drop(columns=
                                                                                                           'model name')
        # Rename the column to include the name of the test
        time_data.rename(columns={'time': f"{test_names[index]}-time"}, inplace=True)

        # Group by model name, and sum over memory, sort so lowest memory first
        memory_data = (((data.groupby(['model name'])['memory'].agg('sum')).sort_values()).reset_index()).drop(
            columns='model name')
        # Rename the column to include the name of the test
        memory_data.rename(columns={'memory': f"{test_names[index]}-memory"}, inplace=True)

        # Join the time and memory dataframes
        memory_time_data = time_data.join(memory_data)

        # Either initialize or add to the combined dataframe for all csvs
        if index == 0:
            combined_df = memory_time_data
            continue
        combined_df = combined_df.join(memory_time_data)

    # Plot the plot
    sns.lineplot(data=combined_df).set(title=f'model checking time and memory per model',
                                       ylabel='seconds or kB',
                                       xlabel='models', yscale="log")
    plt.savefig('../graphs/time-memory_per_model.png')
    plt.clf()
