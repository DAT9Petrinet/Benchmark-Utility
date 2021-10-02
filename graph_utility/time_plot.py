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
    data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
    data = (((data.groupby(['model name'])['time'].agg('sum')).sort_values()).reset_index()).drop('model name', 1)
    data.rename(columns={'time': f"{test_names[index]}"}, inplace=True)
    if index == 0:
        combined_df = data
        continue
    combined_df = combined_df.join(data)

print(combined_df)
sns.lineplot(data=combined_df).set(title=f'Model checking time per model, 16 queries each model',
                                   ylabel='time taken in seconds',
                                   xlabel='models', yscale="log")
plt.savefig(f'graphs/time_per_model.png')
plt.clf()
