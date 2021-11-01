#!/bin/bash

#SBATCH --mail-type=FAIL
#SBATCH --partition=cpu
#SBATCH --mem=15G
#SBATCH -c 2

# Args: <test-name> <binary> <test-folder> <model> <time-out>
# Do not run this. It is supposed to be run by `run_pipeline.sh`, after `reduce_inst.sh` has run. This script will run the
# binary on the given reduced model+query using the query "EF false", forcing it to explore the whole state space.
# The size is then stored in `output/<binary>/<test-name>/<model>.<query>.size`

NAME=$1
BIN=$2
MODEL=$3
TIME_OUT=$4

echo "Exploring state space size of $MODEL"

for MODEL_FILE in $(ls "output/$(basename $BIN)/$NAME" | egrep "$MODEL\.[0-9]+\.pnml$") ; do
	
	Q=$(echo $MODEL_FILE | sed -E "s/.*\.([0-9])+\..*/\1/")
	echo "	Q$Q"

	CMD="./$BIN -q 0 -r 0 output/$(basename $BIN)/$NAME/$MODEL.$Q.pnml -e"

	RES=$(eval "timeout ${TIME_OUT}m $CMD")
	RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
	echo $RES > "output/$(basename $BIN)/$NAME/$MODEL.$Q.sout"

	SIZE=$([[ -n "$(echo $RES | awk "/discovered states/")" ]] && echo $RES | sed -E "s/.*discovered states: *([0-9]+).*/\1/" || echo 0)

	OUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.size"
	rm -f $OUT
	echo $SIZE > $OUT
	
done

exit 0