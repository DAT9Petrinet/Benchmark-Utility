#!/bin/bash

# Args: <binary> [time-out]
# Starts a number of slurm tasks each finding the size of the state space of a model.
# The results will be scattered in a number of `.size` files in `sizes/`

BIN=$1
TIME_OUT=$2
TEST_FOLDER="MCC2021"

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

if [ -z "$TIME_OUT" ] ; then
	echo "No TIME_OUT given, using 24 hours per model"
	TIME_OUT=24
fi


for MODEL in $(ls $TEST_FOLDER) ; do

	sbatch --mail-user=$(whoami) ./measure_base_size_inst.sh $BIN $TEST_FOLDER $MODEL $TIME_OUT
done
