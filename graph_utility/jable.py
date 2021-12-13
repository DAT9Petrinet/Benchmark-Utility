from pathlib import Path

import pandas as pd

root = Path(__file__).parent.parent
data_dir = root / "results"

csvs = [pd.read_csv(csv) for csv in data_dir.glob("*.csv")]
exp_names = [csv.stem for csv in data_dir.glob("*.csv")]

for i, csv in enumerate(csvs):
    csv.set_index(["model name", "query index"], inplace=True)
    csv.rename(columns={col: f"{exp_names[i]}@{col}" for col in csv.columns}, inplace=True)
everything = pd.concat(csvs, axis=1)
everything.sort_index(level=0, inplace=True)

everything_dir = root / "results" / "everything"
everything_dir.mkdir(exist_ok=True)
everything.to_csv(everything_dir / "everything_dk.csv", sep=";", decimal=",")
everything.to_csv(everything_dir / "everything.csv")
