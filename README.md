# Benchmark Utility

Benchmark utility scripts for reduction rules of Petri nets in verifypn.

## Structure
```
output/<test-name>.csv
<binaries>
run_tests.sh
```

## Usage
1) Upload binary called `verifypn-linux64` using `scp`. E.g. `scp cmake-build-wsl-debug/verifypn-linux64 naje17@student.aau.dk@deismcc:~/dat9/red/bench/`
2) Run `sbatch run_test.sh <test-name> <binary-options> [test-time-out]`
3) See more slurm options here: https://github.com/DEIS-Tools/DEIS-MCC/blob/main/usage/CHEAT-SHEET.md

## run_test.sh
Arguments: `<test-name> <binary-options> [test-time-out]`
Runs the binary with the options `binary-options` and collects the stats of each test instance (model+query) in `output/<test-name>.csv`. The `test-name` is used to identify the run. Main task:
- run test
- gather stats using regex on output
- put stats into csv

## The output.csv files
Columns:
- model name
- query index
- time
- memory
- answer (TRUE/FALSE/NONE)
- solved by query simplification (TRUE/FALSE)
- prev place count
- prev transition prev
- post reduced place count
- post reduced transition count
- ruleX (for each application of rule X)

If the query did not finish within the time limit, answer will be NONE. Some queries can be solved using only query simplification which means prev/post transition/place count and rule applications will be 0.
