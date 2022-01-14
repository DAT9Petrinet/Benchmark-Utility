#!/bin/bash

#SBATCH --time=12:00:00
#SBATCH --mail-type=FAIL
#SBATCH --exclude=naples0[1-2]
#SBATCH --mem=15G
#SBATCH -c 2

# Args: <test-name> <binary> <test-folder> <model> <category> <red-time-out> <veri-time-out> <expl-time-out> <bin-options>

echo "Arguments: $@"

NAME=$1
BIN=$2
TEST_FOLDER=$3
MODEL=$4
CATEGORY=$5
RED_TIME_OUT=$6
VERI_TIME_OUT=$7
EXPL_TIME_OUT=$8
OPTIONS="$9"

SCRATCH="/scratch/$(whoami)/$NAME/$MODEL/$CATEGORY"

LTLFLAG=$([[ "$CATEGORY" == "LTLCardinality" ]] && echo " -ltl" || echo "")

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/$CATEGORY.xml" | wc -l)

echo "Processing $MODEL ($NQ queries total)"

for Q in $(seq 1 $NQ) ; do
	
	echo "Q$Q"

	mkdir -p $SCRATCH
	PNML="$SCRATCH/$MODEL.$Q.pnml"

	# ===================== REDUCTION ========================

	echo "  Reduction ..."

	RCMD="./$BIN $OPTIONS -d $RED_TIME_OUT -q 0 -x $Q $LTLFLAG $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$CATEGORY.xml --write-reduced $PNML --noverify"
	ROUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.rout"
	
	# Reduce model+query and store stdout

	O=$(eval "$RCMD")
	echo "$O" > "$ROUT"

	# ===================== VERIFICATION =====================

	echo "  Verification ..."

	VCMD="./$BIN -r 0 -x $Q $LTLFLAG $PNML $TEST_FOLDER/$MODEL/$CATEGORY.xml"
	VOUT="output/$(basename $BIN)/$NAME/$MODEL.$Q.vout"
	
	# Verify query and store stdout along with time and memory spent between @@@s
	O=$(eval "/usr/bin/time -f '@@@%e,%M@@@' timeout ${VERI_TIME_OUT}m $VCMD")
	echo "$O" > "$VOUT"

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
