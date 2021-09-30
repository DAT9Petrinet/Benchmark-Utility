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
num_rows = len(data_list[0].index)

pre_sizes_numerator = [] * num_rows
post_sizes_numerator = [] * num_rows
for index, row in data_list[0].iterrows():
    pre_sizes_numerator.append(int(row['prev place count'] + row['prev transition count']))
    post_sizes_numerator.append(int(row['post place count'] + row['post transition count']))

df = pd.DataFrame()
for test_index, data in enumerate(data_list[1:]):
    ratios = [] * num_rows
    for index, row in data.iterrows():
        size_pre_reductions = int(row['prev place count'] + row['prev transition count'])
        size_post_reductions = int(row['post place count'] + row['post transition count'])

        if size_pre_reductions != pre_sizes_numerator[index]:
            raise Exception("Shits fucked, not comparing same rows")

        ratio = post_sizes_numerator[index] / size_post_reductions
        ratios.append(ratio)

    df[f"{test_names[0]}/{test_names[test_index + 1]}"] = ratios

plot = sns.lineplot(data=df)
plot.set(xlabel='test_instances', ylabel='size ratios', yscale="log")
plt.legend(title='Ratios', loc='upper left')
plot.set(xticks=list(range(0, num_rows)))
plt.savefig('graphs/size_ratios.png')
