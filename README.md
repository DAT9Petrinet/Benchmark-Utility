# Benchmark Utility

Benchmark utility scripts for reduction rules of Petri nets in verifypn.

## Default pipeline

![Benchmark Flowchart](https://imgur.com/CjDag40.png)

## Default pipeline in TAPAAL
![Benchmark Flowchart tapaal](https://i.imgur.com/Cn1eKch.png)

### Structure
```
saved/*
sizes/*
output/<test-name>.csv
binaries/*
explore_inst.sh
measure_base_size.sh
measure_base_size_inst.sh
reduce_inst.sh
run_pipeline.sh
verify_inst.sh
```

### Usage
To run the whole pipeline (including reduction, verification, and state space exploration):

1) Upload binary to `binaries/`using `scp`. E.g. `scp cmake-build-wsl-debug/verifypn-linux64 naje17@student.aau.dk@deismcc:~/dat9/red/bench/binaries/`
1) Run `./run_pipeline.sh <test-name> <binary> <binary-options> [red-time-out] [veri-time-out] [expl-time-out]`
1) See more slurm options here: https://github.com/DEIS-Tools/DEIS-MCC/blob/main/usage/CHEAT-SHEET.md
1) Once all jobs are done, the result is now in stored in `output/<binary>/<test-name>.csv`
1) You may want to remove all the `slurm-*.out`

Verification and/or state space exploration can be disabled by setting their time-out to 0.

#### run_pipeline.sh
Arguments: `<test-name> <binary> <binary-options> [test-time-out]`

Starts a number of slurm jobs each solving the queries of one model in the test folder.
Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
When all jobs are done, the results are compiled into a single csv.

#### reduce_inst.sh
Arguments: `<test-name> <binary> <test-folder> <model> <time-out> <bin-options>`

Do not run this. It is supposed to be run by `run_pipeline.sh`.
This script will reduce the given model in the context of all the (ReachabilityCardinality) queries and
store the raw output in `output/<binary>/<test-name>/<model>.<query>.rout` as well as the reduced net
in `output/<binary>/<test-name>/<model>.<query>.pnml`

#### verify_inst.sh
Arguments: `<test-name> <binary> <test-folder> <model> <time-out>`

Do not run this. It is supposed to be run by `run_pipeline.sh`, after `reduce_inst.sh` has run.
This script will verify the queries for the given model using the reduced net `output/<binary>/<test-name>/<model>.<query>.pnml`.
The raw output of the binary will be stored at `output/<binary>/<test-name>/<model>.<query>.vout`

##### verify_all.sh
Arguments: `<test-name> <binary> [time-out]`

Starts a number of slurm jobs each solving the queries of the reduced nets.
This does not start `compile_results.sh` afterwards.

#### explore_inst.sh
Arguments: `<test-name> <binary> <test-folder> <model> <time-out>`

Do not run this. It is supposed to be run by `run_pipeline.sh`, after `reduce_inst.sh` has run. This script will run the
binary on the given reduced model+query using the query "EF false", forcing it to explore the whole state space.
The size is then stored in `output/<binary>/<test-name>/<model>.<query>.size`

##### explore_all.sh
Arguments: `<test-name> <binary> [time-out]`

Starts a number of slurm jobs each exploring the state spaces of the reduced nets in order to find their size.
This does not start `compile_results.sh` afterwards.

#### compile_results.sh
Arguments: `<test-name> <binary>`

This is the last step of `run_pipeline.sh`, but can also be run manually.
This script will collect the data from all the raw output and size files belonging to the given test into a single `<binary>/<binary>/<test-name>.csv`.

#### The output.csv files
Columns:
- model name
- query index
- verifcation time
- verifcation memory
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

## State space size of unreduced nets

### measure_base_size.sh
Args: `<binary> [time-out]`

Starts a number of slurm tasks each finding the size of the state space of a model (not reduced).
The results will be scattered in a number of `.size` files in `sizes/`.
Hopefully this script only needs to be run once, since the base size of the models never change.

### measure_base_size_inst.sh
Args: `<binary> <test-folder> <model> <time-out>`

Do not run this. It is supposed to be run by `measure_base_size.sh`. This script will run the binary on all the models using the query "EF false",
forcing it to explore the whole state space. The size is then stored in `sizes/<model>.size`
