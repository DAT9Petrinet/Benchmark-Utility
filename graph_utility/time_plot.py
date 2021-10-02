import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]

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

sns.lineplot(data=combined_df).set(title=f'Model checking time and memory per model, 16 queries each model',
                                   ylabel='',
                                   xlabel='models', yscale="log")
plt.savefig(f'graphs/time-memory_per_model.png')
plt.clf()
