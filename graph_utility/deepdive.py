from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

root = Path(__file__).parent.parent
everything_csv_file = root / "saved" / "everything" / "everything.csv"
data = pd.read_csv(everything_csv_file).set_index(["model name", "query index"])

# Filter out irrelevant
data = data[data["base-rules@answer"] != "NONE"]
data = data[data["with-r@answer"] != "NONE"]

# Filter out easy queries
data = data[data["base-rules@verification time"] >= 1.0]
data = data[data["with-r@verification time"] >= 1.0]

print("base-rules known state space sizes", len(data[data["base-rules@state space size"] >= 1]))
print("with-r known state space sizes", len(data[data["with-r@state space size"] >= 1]))

# Filter out queries where state space size is same or bad
data = data[data["with-r@state space size"] > 0]
data = data[data["base-rules@state space size"] > data["with-r@state space size"]]

# New column to find where R is fast/slow
data["veri time ratio"] = data["base-rules@verification time"] / data["with-r@verification time"]
#data = data.sort_values(by=["veri time ratio"])

data = data[data["base-rules@state space size"] >= 1]
data = data[data["with-r@state space size"] >= 1]
data["state space ratio"] = data["base-rules@state space size"] / data["with-r@state space size"]
data = data.sort_values(by=["state space ratio"])

print(data)

# Results
print("WORST")
print(data[:10])

print("BEST")
print(data[-10:])

df = data.reset_index()
g = sns.lineplot(data=df, x=df.index, y="veri time ratio")
#g.set(yscale="log")
plt.show()
