#!/bin/bash

# Args: <test-name> <bin-options> [time-out]
# Starts a number of slurm tasks each solving the queries of one model in the test folder.
# The results will be scattered in a number of csv files. Use collect_and_clean.sh afterwards.

NAME=$1
OPTIONS=$2
TIME_OUT="$3"
BIN="binaries/verifypn-linux64"
TEST_FOLDER="MCC2021"

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$OPTIONS" ] ; then
	echo "Missing options"
	exit
fi

if [ -z "$TIME_OUT" ] ; then
	echo "No TIME_OUT given, using 10 minute per query"
	TIME_OUT=10
fi


for MODEL in $(ls $TEST_FOLDER) ; do

	sbatch --mail-user=$(whoami) ./run_tests.sh $NAME $BIN $TEST_FOLDER $MODEL $TIME_OUT $OPTIONS
done