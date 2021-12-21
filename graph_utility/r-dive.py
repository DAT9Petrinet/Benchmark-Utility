from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

root = Path(__file__).parent.parent
data_dir = root / "results"
MAX = 2000000


def total_time_ratio(row):
    base_total = row['base-rules@verification time'] + row['base-rules@reduce time']
    with_r_total = row['with-r-last@verification time'] + row['with-r-last@reduce time']
    if not (base_total > 0 and with_r_total > 0):
        return np.nan

    if row['with-r-last@answer'] == 'NONE' and row['base-rules@answer'] == 'NONE':
        return np.nan
    elif row['base-rules@answer'] != 'NONE' and row['with-r-last@answer'] == 'NONE':
        return np.nan
    elif row['base-rules@answer'] == 'NONE' and row['with-r-last@answer'] != 'NONE':
        return np.nan
    else:
        return min(base_total / with_r_total, MAX)


def ratio(row):
    if (row['base-rules@verification time'] > 0.0 and row['with-r-last@verification time'] > 0.0):
        if (row['base-rules@verification time'] / row['with-r-last@verification time'] < MAX):
            return row['base-rules@verification time'] / row['with-r-last@verification time']
        else:
            return MAX
    elif row['with-r-last@answer'] == 'None' and row['base-rules@answer'] == 'None':
        return np.nan
    elif row['base-rules@answer'] != 'None' and row['with-r-last@answer'] == 'None':
        return 0
    elif row['base-rules@answer'] == 'None' and row['with-r-last@answer'] != 'None':
        return 100


MAX_USAGE = 20000

csvs = [pd.read_csv(csv) for csv in data_dir.glob("*.csv")]
exp_names = [csv.stem for csv in data_dir.glob("*.csv")]

for i, csv in enumerate(csvs):
    csv.set_index(["model name", "query index"], inplace=True)
    csv.rename(columns={col: f"{exp_names[i]}@{col}" for col in csv.columns}, inplace=True)
everything = pd.concat(csvs, axis=1)
everything.sort_index(level=0, inplace=True)

everything = everything[
    ['base-rules@verification time', 'with-r-last@verification time', 'with-r-last@rule R', 'with-r-last@answer',
     'base-rules@answer', 'base-rules@reduce time', 'with-r-last@reduce time']]

everything = everything[everything['with-r-last@rule R'] < MAX_USAGE]

everything['r-base-ratio'] = everything.apply(
    lambda row: total_time_ratio(row), axis=1)
everything.dropna(inplace=True)
everything.sort_values('with-r-last@rule R', inplace=True)

print(f'i: {MAX_USAGE}, median: {everything["r-base-ratio"].median()}, avg: {everything["r-base-ratio"].mean()}')
print(everything.sort_values("r-base-ratio"))
everything_dir = root / "results" / "everything"
everything_dir.mkdir(exist_ok=True)
everything.to_csv(everything_dir / "r-dive.csv")

everything = everything[['r-base-ratio', 'with-r-last@rule R']]
everything.plot(x='with-r-last@rule R', y='r-base-ratio', kind='scatter')
plt.yscale('log')
plt.show()

X = everything[['with-r-last@rule R']]
y = everything[['r-base-ratio']]

regressor = LinearRegression()

regressor.fit(X, y)

y_pred = regressor.predict(X)
print(f"regressor score: {regressor.score(X, y)}")
print(f"params: {regressor.coef_}")

plt.scatter(X, y, color='red')
plt.plot(X, regressor.predict(X), color='blue')
plt.xlabel('with-r-last@rule R')
plt.ylabel('r-base-ratio')
plt.yscale('linear')
plt.show()
