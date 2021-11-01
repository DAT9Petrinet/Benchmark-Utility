#!/bin/bash

#SBATCH --mail-type=FAIL
#SBATCH --partition=cpu
#SBATCH --mem=15G
#SBATCH -c 2

# Args: <binary> <test-folder> <model> <time-out>
# Do not run this. It is supposed to be run by `measure_base_size.sh`. This script will run the binary on all the models using the query "EF false",
# forcing it to explore the whole state space. The size is then stored in `sizes/<model>.size`

BIN=$1
TEST_FOLDER=$2
MODEL=$3
TIME_OUT=$4

echo "Measuring state space size of $MODEL"

CMD="./$BIN -q 0 -r 0 $TEST_FOLDER/$MODEL/model.pnml -e"
OUT="sizes/$MODEL.size"

rm -f $OUT

RES=$(timeout ${TIME_OUT}h $CMD)
RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
SIZE=$([[ -n "$(echo $RES | awk "/discovered states/")" ]] && echo $RES | sed -E "s/.*discovered states: *([0-9]+).*/\1/" || echo 0)

echo $SIZE > $OUT

exit 0
