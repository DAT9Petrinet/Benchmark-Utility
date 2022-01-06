#!/bin/bash

#SBATCH --time=12:00:00
#SBATCH --mail-type=FAIL
#SBATCH --exclude=naples0[1-2]
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary> <test-folder> <model> <red-time-out> <veri-time-out> <expl-time-out> <bin-options>

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
RED_TIME_OUT=$5
VERI_TIME_OUT=$6
EXPL_TIME_OUT=$7
OPTIONS="$8"

SCRATCH="/scratch/naje17/$NAME/$MODEL"

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/ReachabilityCardinality.xml" | wc -l)

echo "Processing 8 queries of $MODEL ($NQ queries total)"

for Q in $(seq 1 8) ; do
	
	echo "Q$Q"

	mkdir -p $SCRATCH
	PNML="$SCRATCH/$MODEL.$Q.pnml"

	# ===================== REDUCTION ========================

	echo "  Reduction ..."

	RCMD="./$BIN $OPTIONS -d $RED_TIME_OUT -q 0 -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml --write-reduced $PNML --noverify"
	ROUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.rout"
	
	# Reduce model+query and store stdout
	eval "$RCMD" &> "$ROUT"

	# ===================== VERIFICATION =====================

	echo "  Verification ..."

	VCMD="./$BIN -r 0 -x $Q $PNML $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml"
	VOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.vout"
	
	# Verify query and store stdout along with time and memory spent between @@@s
	eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${VERI_TIME_OUT}m $VCMD" &> "$VOUT"

	# ===================== EXPLORATION ======================

	echo "  Exploration ..."

	ECMD="./$BIN -q 0 -r 0 $PNML -e"
	SOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.sout"
	ZOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.size"

	RES=$(eval "timeout ${EXPL_TIME_OUT}m $ECMD")
	RES=$(echo $RES | grep -v "^<" | tr '\n' '\r')
	echo $RES > $SOUT

	SIZE=$([[ -n "$(echo $RES | awk "/explored states/")" ]] && echo $RES | sed -E "s/.*explored states: *([0-9]+).*/\1/" || echo 0)
	
	echo $SIZE > $ZOUT
	
done

echo "Cleaning /scratch"

rm -r $SCRATCH

exit 0
