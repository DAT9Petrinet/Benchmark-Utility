import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

data_list = [pd.read_csv(path) for path in paths]
num_rows = len(data_list[0].index)

for index, data in enumerate(data_list):
    try:
        num_solved_by_simplification = data['solved by query simplification'].value_counts()['TRUE']
    except:
        num_solved_by_simplification = 0
    try:
        num_not_answered_by_simplification = data['solved by query simplification'].value_counts()['FALSE']
    except:
        num_not_answered_by_simplification = 0
    max_y_tick = max(num_solved_by_simplification, num_not_answered_by_simplification)
    sns.countplot(data=data, x='solved by query simplification').set(
        title=f'{test_names[index]}-solved by simplification', xlabel='')
    plt.savefig(f'graphs/solved_by_simplification_{test_names[index]}.png')
    plt.clf()
