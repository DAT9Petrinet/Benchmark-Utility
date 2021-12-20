from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).parent.parent
data_dir = root / "results"



MAX = 2000000000


# MAX = 200
def ratio(row):
    if (row['base-rules@verification time'] > 0 and row['with-r-last@verification time'] > 0):
        if (row['base-rules@verification time'] / row['with-r-last@verification time'] < MAX):
            return row['base-rules@verification time'] / row['with-r-last@verification time']
        else:
            return MAX
    elif row['with-r-last@answer'] != 'None':
        return np.nan
    elif row['base-rules@answer'] != 'None':
        return 0
    elif row['with-r-last@answer'] == 'None' and row['base-rules@answer'] == 'None':
        return np.nan
    else:
        raise Exception("oh no")

max_mean = 0
max_median = 0
mean_index = 0
median_index = 0

for i in range(1, 18896,20):
    csvs = [pd.read_csv(csv) for csv in data_dir.glob("*.csv")]
    exp_names = [csv.stem for csv in data_dir.glob("*.csv")]

    for i, csv in enumerate(csvs):
        csv.set_index(["model name", "query index"], inplace=True)
        csv.rename(columns={col: f"{exp_names[i]}@{col}" for col in csv.columns}, inplace=True)
    everything = pd.concat(csvs, axis=1)
    everything.sort_index(level=0, inplace=True)

    everything = everything[
        ['base-rules@verification time', 'with-r-last@verification time', 'with-r-last@rule R', 'with-r-last@answer',
         'base-rules@answer']]

    everything = everything[everything['with-r-last@rule R'] < i]

    everything['r-base-ratio'] = everything.apply(
        lambda row: ratio(row), axis=1)
    everything.dropna(inplace=True)
    everything.sort_values('with-r-last@rule R', inplace=True)

    if everything["r-base-ratio"].median() > max_median:
        max_median = everything["r-base-ratio"].median()
        median_index = i

    if everything["r-base-ratio"].mean() > max_mean:
        print("hi")
        max_mean = everything["r-base-ratio"].mean()
        mean_index = i
    print(f'i: {i}, median: {everything["r-base-ratio"].median()}, avg: {everything["r-base-ratio"].mean()}')

print(f"max mean {max_mean} at {mean_index}")
print(f"max mean {max_median} at {median_index}")
'''
ratios_sorted = everything.sort_values('r-base-ratio')
print(ratios_sorted['r-base-ratio'])

everything_dir = root / "results" / "everything"
everything_dir.mkdir(exist_ok=True)
everything.to_csv(everything_dir / "r-dive.csv")

everything = everything[['r-base-ratio', 'with-r-last@rule R']]
everything.plot(x='with-r-last@rule R', y='r-base-ratio')
plt.yscale('log')
plt.show()

X = everything[['with-r-last@rule R']]
y = everything[['r-base-ratio']]

regressor = LinearRegression()

regressor.fit(X, y)

y_pred = regressor.predict(X)

plt.scatter(X, y, color='red')
plt.plot(X, regressor.predict(X), color='blue')
plt.xlabel('with-r-last@rule R')
plt.ylabel('r-base-ratio')
plt.yscale('linear')
plt.show()
'''