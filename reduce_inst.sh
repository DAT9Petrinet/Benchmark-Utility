#!/bin/bash

#SBATCH --time=4:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary> <test-folder> <model> <time-out> <bin-options>
# Do not run this. It is supposed to be run by `run_pipeline.sh`.
# This script will reduce the given model in the context of all the (ReachabilityCardinality) queries and
# store the raw output in `output/<binary>/<test-name>/<model>.<query>.rout` as well as the reduced net
# in `output/<binary>/<test-name>/<model>.<query>.pnml`

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
TIME_OUT=$5
OPTIONS="$6"

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/ReachabilityCardinality.xml" | wc -l)

echo "Reducing $MODEL ($NQ queries)"

for Q in $(seq 1 $NQ) ; do
	
	echo "	Q$Q"

	CMD="./$BIN $OPTIONS -d $TIME_OUT -q 0 -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml --write-reduced output/$(basename $BIN)/$NAME/$MODEL.$Q.pnml --noverify"
	OUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.rout"
	
	# Reduce model+query and store stdout
	O=$(eval "$CMD")
	eval "$O" > "$OUT"
	
done

exit 0
