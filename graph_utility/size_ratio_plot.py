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

data_list = [pd.read_csv(path) for path in paths]
num_rows = len(data_list[0].index)

ignore_rows = set()
back_track = 0
for data in data_list:
    for index, row in data.iterrows():
        if index in ignore_rows:
            continue
        if row['answer'] == 'NONE' or row['solved by query simplification']:
            back_track = back_track + 1
            ignore_rows.add(index)

pre_sizes_numerator = [] * num_rows
post_sizes_numerator = [] * num_rows
for index, row in data_list[0].iterrows():
    pre_sizes_numerator.append(int(row['prev place count'] + row['prev transition count']))
    post_sizes_numerator.append(int(row['post place count'] + row['post transition count']))

df = pd.DataFrame()
for test_index, data in enumerate(data_list[1:]):
    ratios = [] * num_rows
    for index, row in data.iterrows():
        if index in ignore_rows:
            continue
        size_pre_reductions = int(row['prev place count'] + row['prev transition count'])

        if size_pre_reductions != pre_sizes_numerator[index]:
            raise Exception("Not comparing same rows")

        size_post_reductions = int(row['post place count'] + row['post transition count'])
        ratio = post_sizes_numerator[index] / size_post_reductions
        ratios.append(ratio)

    df[f"{test_names[0]}/{test_names[test_index + 1]}"] = ratios

sns.lineplot(data=df).set(xlabel='test instances', ylabel='size ratios', yscale="log",
                          xticks=list(range(0, num_rows - len(ignore_rows))), title='Reduced size of nets')
plt.savefig('graphs/size_ratios.png')
plt.clf()
