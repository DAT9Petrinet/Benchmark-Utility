#!/bin/bash

#SBATCH --mail-type=FAIL
#SBATCH --partition=cpu
#SBATCH --mem=15G
#SBATCH -c 2

# Args: <test-name> <binary> <test-folder> <model> <time-out>
# Do not run this. It is supposed to be run by `run.sh` after the `run_test.sh` job is done. This script will run the binary on
# the given reduced net using the query "EF false", forcing it to explore the whole state space.
# The size is then stored in `output/<binary>/<test-name>/<model>.size` and picked up by `compile_results.sh`

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
TIME_OUT=$5

QUERY="sizes/query.xml"

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/ReachabilityCardinality.xml" | wc -l)

echo "Measuring state space size of reduced $MODEL ($NQ queries)"

for Q in $(seq 1 $NQ) ; do

	echo "	Q$Q"

	CMD="./$BIN -q 0 -r 0 -x 1 output/$(basename $BIN)/$NAME/$MODEL.$Q.pnml $QUERY"

	RES=$("timeout ${TIME_OUT}h $CMD")
	RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
	SIZE=$([[ -n "$(echo $RES | awk "/discovered states/")" ]] && echo $RES | sed -E "s/.*discovered states: *([0-9]+).*/\1/" || echo 0)

	OUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.size"
	rm -f $OUT
	echo $SIZE > $OUT
	
done

exit 0