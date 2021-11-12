#!/bin/bash

# Args: <binary> [test-folder] [time-out]
# Starts a number of slurm tasks each finding the size of the state space of a model.
# The results will be scattered in a number of `.size` files in `sizes/`

BIN=$1
TEST_FOLDER=$2
TIME_OUT=$3

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021"
	TEST_FOLDER="MCC2021"
fi

if [ -z "$TIME_OUT" ] ; then
	echo "No TIME_OUT given, using 4 hours per model"
	TIME_OUT=4
fi


for MODEL in $(ls $TEST_FOLDER) ; do

	sbatch --mail-user=$(whoami) ./measure_base_size_inst.sh $BIN $TEST_FOLDER $MODEL $TIME_OUT
done
