#!/bin/bash

# Args: <test-name> <bin-options> [time-out]

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