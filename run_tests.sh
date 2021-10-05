#!/bin/bash

#SBATCH --time=22:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary> <test-folder> <model> <time-out> <bin-options>
# Do not run this. It is supposed to be run by `run.sh`. This script will run the binary on all the (ReachabilityCardinality) queries of a given model
# and store the resulting stats in `output/<test-name>.<model>.csv`

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
TIME_OUT=$5
OPTIONS="$6"


# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/ReachabilityCardinality.xml" | wc -l)

echo "Running $MODEL ($NQ queries)"

for Q in $(seq 1 $NQ) ; do
	
	echo "	Q$Q"
	CMD="./$BIN $OPTIONS -q 0 -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml"
	
	OUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.out"
	
	# Execute test and store stdout along with time and memory spent between @@@s
	eval "/usr/bin/time -f "@@@%e,%M@@@" timeout ${TIME_OUT}m $CMD" &> "$OUT"
	
done

exit 0
