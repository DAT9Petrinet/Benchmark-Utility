import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot(data_list, test_names):
    sns.set_style("whitegrid")
    combined_df = pd.DataFrame()
    for index, data in enumerate(data_list):
        time_data = data
        time_data = time_data.drop(
            time_data[(time_data['solved by query simplification']) | (time_data.answer == 'NONE')].index)
        time_data = (((time_data.groupby(['model name'])['time'].agg('sum')).sort_values()).reset_index()).drop(
            'model name', 1)
        time_data.rename(columns={'time': f"{test_names[index]}-time"}, inplace=True)

        memory_data = data
        memory_data = memory_data.drop(
            memory_data[(memory_data['solved by query simplification']) | (memory_data.answer == 'NONE')].index)
        memory_data = (((memory_data.groupby(['model name'])['memory'].agg('sum')).sort_values()).reset_index()).drop(
            'model name', 1)
        memory_data.rename(columns={'memory': f"{test_names[index]}-memory"}, inplace=True)

        memory_time_data = time_data.join(memory_data)
        if index == 0:
            combined_df = memory_time_data
            continue
        combined_df = combined_df.join(memory_time_data)

    sns.lineplot(data=combined_df).set(title=f'model checking time and memory per model',
                                       ylabel='seconds or kB',
                                       xlabel='models', yscale="log")
    plt.savefig('../graphs/time-memory_per_model.png')
    plt.clf()
