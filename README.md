# Benchmark Utility

Benchmark utility scripts for reduction rules of Petri nets in verifypn.

## Structure
```
saved/
output/<test-name>.csv
binaries/verifypn-linux
run_tests.sh
run.sh
```

## Usage
1) Upload binary called `verifypn-linux64` to `binaries/`using `scp`. E.g. `scp cmake-build-wsl-debug/verifypn-linux64 naje17@student.aau.dk@deismcc:~/dat9/red/bench/binaries/`
1) Run `./run.sh <test-name> <binary-options> [test-time-out]`
1) See more slurm options here: https://github.com/DEIS-Tools/DEIS-MCC/blob/main/usage/CHEAT-SHEET.md
1) Once the jobs are done, run `./collect_and_clean.sh <test-name>`
1) The result is now in stored in `output/<test-name>.csv`
1) You may want to remove all the `slurm-*.out`

## run.sh
Arguments: `<test-name> <binary> <binary-options> [test-time-out]`

Starts a number of slurm tasks each solving the queries of one model in the test folder.
The results will be scattered in a number of csv files. Use `collect_and_clean.sh` afterwards.

## run_tests.sh
Arguments: `<test-name> <binary> <test-folder> <model> <time-out> <bin-options>`

Do not run this. It is supposed to be run by `run.sh`.
This script will run the binary on all the (ReachabilityCardinality) queries of a given model and
store the resulting stats in `output/<test-name>.<model>.csv`

## compile_results.sh
Arguments: `<test-name> <binary>`

After running `run.sh` the results will be scattered in a number of `.out` files.
This script will collect the data from all the files belong to the given test into a single `<binary>/<test-name>.csv`.

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
- rule X (number of applications of rule X)

If the query did not finish within the time limit, answer will be NONE. Some queries can be solved using only
query simplification which means prev/post transition/place count and rule applications will be 0.
