# Benchmark Utility

Benchmark utility scripts for reduction rules of Petri nets in verifypn.

## Structure
```
saved/*
sizes/*
output/<test-name>.csv
binaries/*
run_tests.sh
run.sh
measure_base_size.sh
measure_base_size_inst.sh
measure_reduced_size_inst.sh
```

## Usage
1) Upload binary to `binaries/`using `scp`. E.g. `scp cmake-build-wsl-debug/verifypn-linux64 naje17@student.aau.dk@deismcc:~/dat9/red/bench/binaries/`
1) Run `./run.sh <test-name> <binary> <binary-options> [test-time-out]`
1) See more slurm options here: https://github.com/DEIS-Tools/DEIS-MCC/blob/main/usage/CHEAT-SHEET.md
1) Once all jobs are done, the result is now in stored in `output/<binary>/<test-name>.csv`
1) You may want to remove all the `slurm-*.out`

### run.sh
Arguments: `<test-name> <binary> <binary-options> [test-time-out]`

Starts a number of slurm jobs each solving the queries of one model in the test folder.
Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
When all jobs are done, the results are compiled into a single csv.

### run_tests.sh
Arguments: `<test-name> <binary> <test-folder> <model> <time-out> <bin-options>`

Do not run this. It is supposed to be run by `run.sh`.
This script will run the binary on all the (ReachabilityCardinality) queries of a given model and
store the raw output in `output/<binary>/<test-name>/<model>.<query>.out`

### measure_reduced_size_inst.sh
Args: `<test-name> <binary> <test-folder> <model> <time-out>`

Do not run this. It is supposed to be run by `run.sh` after the `run_test.sh` job is done. This script will run the binary on
the given reduced net using the query "EF false", forcing it to explore the whole state space.
The size is then stored in `output/<binary>/<test-name>/<model>.size` and picked up by `compile_results.sh`

### compile_results.sh
Arguments: `<test-name> <binary>`

This is the last step of `run.sh`, but can also be run manually.
This script will collect the data from all the raw output and size files belonging to the given test into a single `<binary>/<binary>/<test-name>.csv`.

### The output.csv files
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
- reduce time
- state space size
- rule X (number of applications of rule X)

If the query did not finish within the time limit, answer will be NONE. Calculating the state space size may take too long, in which case it will be 0.

## measure_base_size.sh
Args: `<binary> [time-out]`

Starts a number of slurm tasks each finding the size of the state space of a model (not reduced).
The results will be scattered in a number of `.size` files in `sizes/`.
Hopefully this script only needs to be run once, since the base size of the models never change.

### measure_base_size_inst.sh
Args: `<binary> <test-folder> <model> <time-out>`

Do not run this. It is supposed to be run by `measure_base_size.sh`. This script will run the binary on all the models using the query "EF false",
forcing it to explore the whole state space. The size is then stored in `sizes/<model>.size`
