#!/bin/bash

# Args: <test-name> <binary> [time-out]
# Starts a number of slurm jobs each exploring the state spaces of the reduced nets in order to find their size.
# This does not start `compile_results.sh` afterwards.

NAME=$1
BIN=$2
TEST_FOLDER=$3
TIME_OUT=$4

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021"
	TEST_FOLDER="MCC2021"
fi

if [ -z "$TIME_OUT" ] ; then
	echo "No TIME_OUT given, using 10 minute per query"
	TIME_OUT=10
fi

if (( $TIME_OUT < 1 )); then
	echo "Aborting due to TIME_OUT of 0"
	exit
fi

for MODEL in $(ls $TEST_FOLDER) ; do
	sbatch --mail-user=$(whoami) --job-name=$NAME ./explore_inst.sh $NAME $BIN $MODEL $TIME_OUT
done

# sbatch --partition=rome -c 1 --mail-type=FAIL --mail-user=$(whoami) --job-name=$NAME --dependency=singleton ./compile_results.sh $NAME $BIN
