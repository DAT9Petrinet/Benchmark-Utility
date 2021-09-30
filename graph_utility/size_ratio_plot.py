import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os.path

# Takes a number of csv as input
# The first csv will be used as numerator in the plots
sns.set_style("whitegrid")

paths = sys.argv[1:]
test_names = [os.path.split(os.path.splitext(path)[0])[1] for path in paths]

column_names = ['model_name', 'query_index', 'time', 'memory', 'answer', 'prev place count', 'prev transition count',
                'post place count', 'post transition count', 'rule A', 'rule B', 'rule C', 'rule D', 'rule E', 'rule F',
                'rule G', 'rule H', 'rule I', 'rule J', 'rule K', 'rule L']

data_list = [pd.read_csv(path, names=column_names, skiprows=1) for path in paths]
num_rows = len(data_list[0].index)

ignore_rows = set()
for data in data_list:
    for index, row in data.iterrows():
        if row['answer'] == 'None':
            ignore_rows.add(index)

pre_sizes_numerator = [] * num_rows
post_sizes_numerator = [] * num_rows
for index, row in data_list[0].iterrows():
    if index in ignore_rows:
        continue
    else:
        pre_sizes_numerator.append(int(row['prev place count'] + row['prev transition count']))
        post_sizes_numerator.append(int(row['post place count'] + row['post transition count']))

df = pd.DataFrame()
for test_index, data in enumerate(data_list[1:]):
    back_track = 0
    ratios = [] * num_rows
    for index, row in data.iterrows():
        if index in ignore_rows:
            back_track = back_track + 1
            continue
        size_pre_reductions = int(row['prev place count'] + row['prev transition count'])
        size_post_reductions = int(row['post place count'] + row['post transition count'])

        if size_pre_reductions != pre_sizes_numerator[index - back_track]:
            raise Exception("Shits fucked, not comparing same rows")

        ratio = post_sizes_numerator[index - back_track] / size_post_reductions
        ratios.append(ratio)

    df[f"{test_names[0]}/{test_names[test_index + 1]}"] = ratios

sns.lineplot(data=df).set(xlabel='test instances', ylabel='size ratios', yscale="log",
                          xticks=list(range(0, num_rows-len(ignore_rows))), title='Reduced size of nets')
plt.savefig('graphs/size_ratios.png')
plt.clf()
