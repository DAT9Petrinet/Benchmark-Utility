from pathlib import Path

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

root = Path(__file__).parent.parent
everything_csv_file = root / "saved" / "everything" / "everything.csv"
data = pd.read_csv(everything_csv_file).set_index(["model name", "query index"])
rc_types = pd.read_csv(root / "static_data" / "RC_types.csv").set_index(["model name"])
#data = data.merge(rc_types, on=["model name", "query index"])

exp1 = "base-rules"
exp2 = "with-r-last"

print(f"{exp1} answers", len(data[data[f"{exp1}@answer"] != "NONE"]))
print(f"{exp2} answers", len(data[data[f"{exp2}@answer"] != "NONE"]))
print("common answers", len(data[(data[f"{exp1}@answer"] != "NONE") & (data[f"{exp2}@answer"] != "NONE")]))

# Filter out unanswered
#data = data[data[f"{exp1}@answer"] != "NONE"]
#data = data[data[f"{exp2}@answer"] != "NONE"]

# Filter out easy queries
#data = data[(data[f"{exp1}@verification time"] >= 1.0) | (data[f"{exp2}@verification time"] >= 1.0)]

print(f"{exp1} known state space sizes", len(data[data[f"{exp1}@state space size"] >= 1]))
print(f"{exp2} known state space sizes", len(data[data[f"{exp2}@state space size"] >= 1]))

# Filter out queries based on state space size
data = data[data[f"{exp2}@state space size"] > 0]
#data = data[data[f"{exp1}@state space size"] > data[f"{exp2}@state space size"]]
data = data[data[f"{exp1}@state space size"] > 0]

# New column to find where R is faster/slower
data["veri time ratio"] = data[f"{exp1}@verification time"] / data[f"{exp2}@verification time"]

# New column to find where R has reduced more/less
data["state space ratio"] = data[f"{exp1}@state space size"] / data[f"{exp2}@state space size"]

data["net size"] = data[f"{exp1}@prev place count"] + data[f"{exp1}@prev transition count"]

# Instances where R has reduced more but verification is slower
#data = data[data[f"{exp1}@verification time"] < data[f"{exp2}@verification time"]]
#data = data[data[f"{exp1}@state space size"] < data[f"{exp2}@state space size"]]

#positive = ((data[f"{exp1}@answer"] == "TRUE") & (data["type"] == "EF")) | ((data[f"{exp1}@answer"] == "FALSE") & (data["type"] == "AG"))
#negative = ((data[f"{exp1}@answer"] == "FALSE") & (data["type"] == "EF")) | ((data[f"{exp1}@answer"] == "TRUE") & (data["type"] == "AG"))
#data = data[data["model name"].str.contains("Health")]

data = data.sort_values(by=["state space ratio"])
data = data[[
    f"{exp1}@verification time",
    f"{exp2}@verification time",
    "veri time ratio",
    f"{exp1}@state space size",
    f"{exp2}@state space size",
    "state space ratio",
    "net size",
    f"{exp2}@reduce time",
    f"{exp1}@answer",
]]
data = data.reset_index()

data = data.sort_values(by=["state space ratio"])
data.to_csv(root / "out.csv")


df = data.reset_index()
g = sns.lineplot(data=df, x=df.index, y="state space ratio")
g.set(yscale="log")
plt.show()
