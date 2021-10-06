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

OUT="output/$NAME.$MODEL.csv"

append_row() {
	echo \"$1\",\"$2\",\"$3\",\"$4\",\"$5\",\"$6\",\"$7\",\"$8\",\"$9\",\"${10}\",\"${11}\",\"${12}\",\"${13}\",\"${14}\",\"${15}\",\"${16}\",\"${17}\",\"${18}\",\"${19}\",\"${20}\",\"${21}\",\"${22}\",\"${23}\" >> $OUT
}

# Find the number of queries for this model by counting how many times "<property>" appears
NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/ReachabilityCardinality.xml" | wc -l)

echo "Running $MODEL ($NQ queries)"

for Q in $(seq 1 $NQ ) ; do
	
	echo "	Q$Q"
	CMD="./$BIN $OPTIONS -q 0 -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/ReachabilityCardinality.xml"
	echo $CMD
	
	# Execute test and store stdout in RES along with time and memory spent between @@@s
	# We also replace all newline characters \n with the character \r, since sed only works on one line at the time. https://unix.stackexchange.com/a/152389
	eval "/usr/bin/time -f "@@@%e,%M@@@" timeout ${TIME_OUT}m $CMD" &> "output/temp-$NAME-$MODEL"
	RES=$(cat "output/temp-$NAME-$MODEL" | tr '\n' '\r')

	TIME=$(echo $RES | sed -E "s/.*@@@(.*),.*@@@.*/\1/")
	MEM=$(echo $RES | sed -E "s/.*@@@.*,(.*)@@@.*/\1/")

	# Did we get an answer or did the query time out?
	# We can check this by checking if "satisfied" is a substring of the output.
	# If "Query is satisfied" is also a substring, then the answer is TRUE.
	ANSWER=$([[ -n "$(echo $RES | awk '/satisfied/')" ]] && ([[ -n "$(echo $RES | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE") || echo "NONE")

	# Was query solved using query reduction?
	QUERY_SIMPLIFICATION=$([[ -n "$(echo $RES | awk '/Query solved by Query Simplification/')" ]] && echo "TRUE" || echo "FALSE")

	if [[ $ANSWER = "NONE" || $QUERY_SIMPLIFICATION = "TRUE" ]]; then

		# In this case, no structural reduction was performed

		PREV_PLACE_COUNT=0
		PREV_TRANS_COUNT=0
		POST_RED_PLACE_COUNT=0
		POST_RED_TRANS_COUNT=0

		RULE_A=0
		RULE_B=0
		RULE_C=0
		RULE_D=0
		RULE_E=0
		RULE_F=0
		RULE_G=0
		RULE_H=0
		RULE_I=0
		RULE_J=0
		RULE_K=0
		RULE_L=0
		RULE_M=0
	
	else

		PREV_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: ([0-9]+).*/\1/")
		PREV_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: [0-9]+ places, ([0-9]+).*/\1/")
		POST_RED_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/")
		POST_RED_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: [0-9]+ places, ([0-9]+).*/\1/")

		RULE_A=$(echo $RES | sed -E "s/.*Applications of rule A: ([0-9]+).*/\1/")
		RULE_B=$(echo $RES | sed -E "s/.*Applications of rule B: ([0-9]+).*/\1/")
		RULE_C=$(echo $RES | sed -E "s/.*Applications of rule C: ([0-9]+).*/\1/")
		RULE_D=$(echo $RES | sed -E "s/.*Applications of rule D: ([0-9]+).*/\1/")
		RULE_E=$(echo $RES | sed -E "s/.*Applications of rule E: ([0-9]+).*/\1/")
		RULE_F=$(echo $RES | sed -E "s/.*Applications of rule F: ([0-9]+).*/\1/")
		RULE_G=$(echo $RES | sed -E "s/.*Applications of rule G: ([0-9]+).*/\1/")
		RULE_H=$(echo $RES | sed -E "s/.*Applications of rule H: ([0-9]+).*/\1/")
		RULE_I=$(echo $RES | sed -E "s/.*Applications of rule I: ([0-9]+).*/\1/")
		RULE_J=$(echo $RES | sed -E "s/.*Applications of rule J: ([0-9]+).*/\1/")
		RULE_K=$(echo $RES | sed -E "s/.*Applications of rule K: ([0-9]+).*/\1/")
		RULE_L=$(echo $RES | sed -E "s/.*Applications of rule L: ([0-9]+).*/\1/")
		RULE_M=$(echo $RES | sed -E "s/.*Applications of rule M: ([0-9]+).*/\1/")

	fi

	append_row "$MODEL" "$Q" "$TIME" "$MEM" "$ANSWER" "$QUERY_SIMPLIFICATION" "$PREV_PLACE_COUNT" "$PREV_TRANS_COUNT" "$POST_RED_PLACE_COUNT" "$POST_RED_TRANS_COUNT" "$RULE_A" "$RULE_B" "$RULE_C" "$RULE_D" "$RULE_E" "$RULE_F" "$RULE_G" "$RULE_H" "$RULE_I" "$RULE_J" "$RULE_K" "$RULE_L" "$RULE_M"
done

exit 0
