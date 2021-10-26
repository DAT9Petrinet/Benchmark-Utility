#!/bin/bash

# Args: <test-name> <binary> <bin-options> [time-out]
# Starts a number of slurm jobs each solving the queries of one model in the test folder.
# Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
# When all jobs are done, the results are compiled into a single csv.

NAME=$1
BIN=$2
OPTIONS=$3
TIME_OUT=$4
TEST_FOLDER="MCC2021"

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ -z "$OPTIONS" ] ; then
	echo "Missing options"
	exit
fi

if [ -z "$TIME_OUT" ] ; then
	echo "No TIME_OUT given, using 5 minute per query"
	TIME_OUT=5
fi


mkdir -p "output/$(basename $BIN)/$NAME"

for MODEL in $(ls $TEST_FOLDER) ; do
	# Run reductions
	JOB_ID=$(sbatch --mail-user=$(whoami) --job-name=$NAME ./run_tests.sh $NAME $BIN $TEST_FOLDER $MODEL $TIME_OUT "$OPTIONS")

	# Measure state space size of reduced net
	sbatch --mail-user=$(whoami) --job-name=$NAME --dependency=afterany:$JOB_ID ./measure_reduced_size_inst.sh $NAME $BIN $TEST_FOLDER $MODEL 24
done

sbatch --partition=naples -c 1 --mail-type=FAIL --mail-user=$(whoami) --job-name=$NAME --dependency=singleton ./compile_results.sh $NAME $BIN
