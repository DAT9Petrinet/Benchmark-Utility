#!/bin/bash

#SBATCH --time=4:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary> <test-folder> <model> <time-out>
# Do not run this. It is supposed to be run by `run_pipeline.sh`, after `reduce_inst.sh` has run.
# This script will verify the queries for the given model using the reduced net `output/<binary>/<test-name>/<model>.<query>.pnml`.
# The raw output of the binary will be stored at `output/<binary>/<test-name>/<model>.<query>.vout`

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
TIME_OUT=$5

echo "Verifying the reduced nets of $MODEL"

for MODEL_FILE in $(ls "output/$(basename $BIN)/$NAME" | egrep "$MODEL\.[0-9]+\.pnml$") ; do
	
	Q=$(echo $MODEL_FILE | sed -E "s/.*\.([0-9]+)\..*/\1/")
	echo "	Q$Q"

	CMD="./$BIN -r 0 -x $Q output/$(basename $BIN)/$NAME/$MODEL_FILE $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml"
	OUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.vout"
	
	# Verify query and store stdout along with time and memory spent between @@@s
	O=$(eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${TIME_OUT}m $CMD" 2>&1)
	echo "$O" > "$OUT"
	
done

exit 0
