#!/bin/bash

# Args: <test-name> <binary> <bin-options> [test-folder] [red-time-out] [veri-time-out] [expl-time-out]
# Starts a number of slurm jobs each solving the queries of one model in the test folder.
# Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
# When all jobs are done, the results are compiled into a single csv.

NAME=$1
BIN=$2
OPTIONS=$3
TEST_FOLDER=$4
RED_TIME_OUT=$5
VERI_TIME_OUT=$6
EXPL_TIME_OUT=$7

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ ! -f "$BIN" ] ; then
	echo "Binary does not exist"
	exit
fi

if [ -z "$OPTIONS" ] ; then
	echo "Missing binary options"
	exit
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021"
	TEST_FOLDER="MCC2021"
fi

if [ -z "$RED_TIME_OUT" ] ; then
	echo "No RED_TIME_OUT given, using 300 seconds per query"
	RED_TIME_OUT=300
fi

if [ -z "$VERI_TIME_OUT" ] ; then
	echo "No VERI_TIME_OUT given, using 5 minute per query"
	VERI_TIME_OUT=5
fi

if [ -z "$EXPL_TIME_OUT" ] ; then
	echo "No EXPL_TIME_OUT given, using 10 minute per query"
	EXPL_TIME_OUT=10
fi

DIR="output/$(basename $BIN)/$NAME"
rm -rf $DIR
mkdir -p $DIR

if (( $VERI_TIME_OUT < 1 )); then
	echo "No verification jobs will be started, since VERI_TIME_OUT set to 0"
fi

if (( $EXPL_TIME_OUT < 1 )); then
	echo "No exploration jobs will be started, since EXPL_TIME_OUT set to 0"
fi

for MODEL in $(ls $TEST_FOLDER) ; do
	# Run reductions
	JOB_ID=$(sbatch --mail-user=$(whoami) --job-name=$NAME ./reduce_inst.sh $NAME $BIN $TEST_FOLDER $MODEL $RED_TIME_OUT "$OPTIONS" | sed 's/Submitted batch job //')
	echo "Submitted batch job $JOB_ID for $MODEL"

	# Verify reduced net
	if (( $VERI_TIME_OUT > 0 )); then
		sbatch --mail-user=$(whoami) --job-name=$NAME --dependency=afterany:$JOB_ID ./verify_inst.sh $NAME $BIN $TEST_FOLDER $MODEL $VERI_TIME_OUT
	fi

	# Measure state space size of reduced net
	if (( $EXPL_TIME_OUT > 0 )); then
		sbatch --mail-user=$(whoami) --job-name=$NAME --dependency=afterany:$JOB_ID ./explore_inst.sh $NAME $BIN $MODEL $EXPL_TIME_OUT
	fi
done

sbatch --partition=cpu --exclude=naples0[1-9] -c 1 --mail-type=FAIL --mail-user=$(whoami) --job-name=$NAME --dependency=singleton ./compile_results.sh $NAME $BIN
