#!/bin/bash

# Args: <test-name> <binary> <bin-options> [test-folder] [category] [partition] [red-time-out] [veri-time-out] [expl-time-out]
# Starts a number of slurm jobs each solving the queries of one model in the test folder.
# Each of those jobs are then followed by another job running the reduced net too in order to determine the size of the state space.
# When all jobs are done, the results are compiled into a single csv.

NAME=$1
BIN=$2
OPTIONS=$3
TEST_FOLDER=$4
CATEGORY=$5
PARTITION=$6
RED_TIME_OUT=$7
VERI_TIME_OUT=$8
EXPL_TIME_OUT=$9

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
elif [ "$OPTIONS" =~ '^-r [0-4] ' ] ; then
	echo "Err: OPTIONS start with '-r [0-4] '. It is $OPTIONS"
	exit 0
fi

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021"
	TEST_FOLDER="MCC2021"
elif [ "$TEST_FOLDER" != "MCC2021" ] && [ "$TEST_FOLDER" != "MCC2021_inhib" ] ; then
	echo "Err: TEST_FOLDER must be MCC2021 or MCC2021_inhib. It is $TEST_FOLDER"
	exit 0
fi

if [ -z "$CATEGORY" ] ; then
	echo "No CATEGORY given, using ReachabilityCardinality"
	CATEGORY="ReachabilityCardinality"
elif [ "$CATEGORY" != "ReachabilityCardinality" ] && [ "$CATEGORY" != "LTLCardinality" ] && [ "$CATEGORY" != "CTLCardinality" ] ; then
	echo "Err: CATEGORY must be ReachabilityCardinality, LTLCardinality, or CTLCardinality. It is $CATEGORY"
	exit 0
fi

if [ -z "$PARTITION" ] ; then
	echo "No PARTITION given, using naples"
	PARTITION="naples"
elif [ "$PARTITION" != "naples" ] && [ "$PARTITION" != "rome" ] && [ "$PARTITION" != "dhabi" ] && [ "$PARTITION" != "cpu" ] ; then
	echo "Err: PARTITION must be naples, rome, dhabi, or cpu. It is $PARTITION"
	exit 0
fi

if [ -z "$RED_TIME_OUT" ] ; then
	echo "No RED_TIME_OUT given, using 120 seconds per query"
	RED_TIME_OUT=120
elif [ "$RED_TIME_OUT" =~ '^[0-9]+$' ] ; then
	echo "Err: RED_TIME_OUT must be a non-negative integer (seconds). It is $RED_TIME_OUT"
	exit 0
fi

if [ -z "$VERI_TIME_OUT" ] ; then
	echo "No VERI_TIME_OUT given, using 3 minute per query"
	VERI_TIME_OUT=3
elif [ "$VERI_TIME_OUT" =~ '^[0-9]+$' ] ; then
	echo "Err: VERI_TIME_OUT must be a non-negative integer (minutes). It is $VERI_TIME_OUT"
	exit 0
fi

if [ -z "$EXPL_TIME_OUT" ] ; then
	echo "No EXPL_TIME_OUT given, using 4 minute per query"
	EXPL_TIME_OUT=4
elif [ "$EXPL_TIME_OUT" =~ '^[0-9]+$' ] ; then
	echo "Err: EXPL_TIME_OUT must be a non-negative integer (minutes). It is $EXPL_TIME_OUT"
	exit 0
fi

DIR="output/$(basename $BIN)/$NAME"
rm -rf $DIR
mkdir -p $DIR

for MODEL in $(ls $TEST_FOLDER) ; do
	# Process model

	JOB_ID=$(sbatch --mail-user=$(whoami) --job-name=$NAME --partition=$PARTITION ./scratch_inst.sh $NAME $BIN $TEST_FOLDER $MODEL $CATEGORY $RED_TIME_OUT $VERI_TIME_OUT $EXPL_TIME_OUT "$OPTIONS" | sed 's/Submitted batch job //')
	echo "Submitted batch job $JOB_ID for $MODEL"

done

sbatch --partition=rome -c 1 --mail-type=FAIL --mail-user=$(whoami) --job-name=$NAME --dependency=singleton ./compile_results.sh $NAME $BIN
