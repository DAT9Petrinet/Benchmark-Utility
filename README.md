# Benchmark Utility

Benchmark utility scripts for reduction rules of Petri nets in verifypn.

## Structure
```
output/
binaries/
run_tests.sh
```

## Usage
1) Upload binary to `binaries/`
2) run `run_test.sh` using slurm

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
- answer (TRUE/FALSE)
- prev place count
- prev transition prev
- post reduced place count
- post reduced transition count
- ruleX (for each application of rule X)
