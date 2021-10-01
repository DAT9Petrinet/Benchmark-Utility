import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]

for index, data in enumerate(data_list):
    draw_data = data.reset_index().melt(id_vars=['index', 'model name'], var_name='col')
    draw_data['model name'] = draw_data['model name'].astype(str)

    sns.lineplot(x='index',
                 y='value',
                 data=draw_data)
    ##data = data.drop(data[(data['solved by query simplification']) | (data.answer == 'NONE')].index)
    #sns.lineplot(data=data['time'], sort=True).set(title=f'{test_names[index]}-time', ylabel='time taken',
      #                                             xlabel='', yscale="log")
    plt.savefig(f'graphs/time_playground_{test_names[index]}.png')
    plt.clf()
