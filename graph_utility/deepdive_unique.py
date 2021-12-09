from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

root = Path(__file__).parent.parent
everything_csv_file = root / "saved" / "everything" / "everything.csv"
data = pd.read_csv(everything_csv_file).set_index(["model name", "query index"])
rc_types = pd.read_csv(root / "static_data" / "RC_types.csv").set_index(["model name"])

print("base-rules answers", len(data[data["base-rules@answer"] != "NONE"]))
print("with-r answers", len(data[data["with-r@answer"] != "NONE"]))
print("common answers", len(data[(data["base-rules@answer"] != "NONE") & (data["with-r@answer"] != "NONE")]))

# Filter out irrelevant
#data = data[data["base-rules@answer"] == "NONE"]
#data = data[data["with-r@answer"] != "NONE"]

# Filter out easy queries
data = data[data["base-rules@verification time"] >= 0.5]
data = data[data["with-r@verification time"] >= 0.5]

data = data.merge(rc_types, on=["model name", "query index"])

print("base-rules known state space sizes", len(data[data["base-rules@state space size"] > 0]))
print("with-r known state space sizes", len(data[data["with-r@state space size"] > 0]))
print("common state space sizes", len(data[(data["base-rules@state space size"] > 0) & (data["with-r@state space size"] > 0)]))

# Filter out queries where state space size is unknown for both
#data = data[data["base-rules@state space size"] > 0]
#data = data[data["with-r@state space size"] > 0]

only_r = data[(data["base-rules@answer"] == "NONE") & (data["with-r@answer"] != "NONE")]
only_base = data[(data["base-rules@answer"] != "NONE") & (data["with-r@answer"] == "NONE")]

data = pd.concat({"only_r": only_r, "only_base": only_base})

# New column to find where R has reduced more/less
#data["state space ratio"] = data["base-rules@state space size"] / data["with-r@state space size"]
#data = data.sort_values(by=["state space ratio"])

#print(data[["base-rules@verification time", "with-r@verification time"]])

df = data.reset_index()
g = sns.lineplot(data=df, x=df.index, y="with-r@rule R", hue="level_0")
#g.set(yscale="log")
plt.show()
