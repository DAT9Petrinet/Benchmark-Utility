import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

column_names = ['model_name', 'query_index', 'time', 'memory', 'answer', 'prev place count', 'prev transition count',
                'post place count', 'post transition count', 'rule A', 'rule B', 'rule C', 'rule D', 'rule E', 'rule F',
                'rule G', 'rule H', 'rule I', 'rule J', 'rule K', 'rule L']

data_list = [pd.read_csv(path, names=column_names, skiprows=1) for path in paths]

for index, data in enumerate(data_list):

    plt.savefig(f'graphs/memory_{test_names[index]}.png')