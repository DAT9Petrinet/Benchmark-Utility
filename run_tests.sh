#!/bin/bash
#SBATCH --time=22:00:00
#SBATCH --mail-user=$(whoami)
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G

NAME=$1
OPTIONS=$2
TIMING="$3"
BIN="verifypn-linux64"
TEST_FOLDER="MCC2021"

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$OPTIONS" ] ; then
	echo "Missing options"
	exit
fi

if [ -z "$TIMING" ] ; then
	echo "No timing given, using 1 minute per query"
	T=1
fi

OUT="output/$NAME.csv"

write_headers() {
	# First check if the file exists, if not: insert row with headers
	if ! [[ -f "$OUT" ]] 
	then
		col1="model name"
		col2="query index"
		col3="time"
		col4="memory"
		col5="answer"
		col6="prev place count"
		col7="prev transition count"
		col8="post place count"
		col9="post transition count"
		col10="rule A"
		col11="rule B"
		col12="rule C"
		col13="rule D"
		col14="rule E"
		col15="rule F"
		col16="rule G"
		col17="rule H"
		col18="rule I"
		col19="rule J"
		col20="rule K"
		col21="rule L"
		echo \"$col1\",\"$col2\",\"$col3\",\"$col4\",\"$col5\",\"$col6\",\"$col7\",\"$col8\",\"$col9\",\"${col10}\",\"${col11}\",\"${col12}\",\"${col13}\",\"${col14}\",\"${col15}\",\"${col16}\",\"${col17}\",\"${col18}\",\"${col19}\",\"${col20}\",\"${col21}\" >> $OUT
	fi
}

append_row() {
	echo \"$1\",\"$2\",\"$3\",\"$4\",\"$5\",\"$6\",\"$7\",\"$8\",\"$9\",\"${10}\",\"${11}\",\"${12}\",\"${13}\",\"${14}\",\"${15}\",\"${16}\",\"${17}\",\"${18}\",\"${19}\",\"${20}\",\"${21}\" >> $OUT
}

write_headers

for TEST_TYPE in Reachability{Cardinality} ; do
	for MODEL in $(ls $TEST_FOLDER) ; do
		
		echo "Running $MODEL"
		
		# Find the number of queries for this model by counting how many times "<property>" appears
		NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/$TEST_TYPE.xml" | wc -l)

		for Q in $(seq 1 $NQ ) ; do
			
			echo "	Q$Q"
			CMD = "./binaries/$BIN $OPTIONS -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$TEST_TYPE.xml"
			
			# Execute test and store stdout in RES along with time and memory spent between @@@s
			RES=$(eval "/usr/bin/time -f "@@@%e,%M@@@" timeout ${TIMING}m $CMD")

			TIME=$(echo $RES | sed -E "s/.*@@@(.*),.*@@@.*/\1/")
			MEM=$(echo $RES | sed -E "s/.*@@@.*,(.*)@@@.*/\1/")

			ANSWER=$([[ ! -z "$(echo $RES | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE")
			PREV_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: ([0-9]+).*/\1/")
			PREV_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net before[^:]*: [0-9]+.*([0-9]+).*/\1/")
			POST_RED_PLACE_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/")
			POST_RED_TRANS_COUNT=$(echo $RES | sed -E "s/.*Size of net after[^:]*: [0-9]+.*([0-9]+).*/\1/")

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

			append_row $MODEL $Q $TIME $MEM $ANSWER $PREV_PLACE_COUNT $PREV_TRANS_COUNT $POST_RED_PLACE_COUNT $POST_RED_TRANS_COUNT $RULE_A $RULE_B $RULE_C $RULE_D $RULE_D $RULE_E $RULE_F $RULE_G $RULE_H $RULE_I $RULE_J $RULE_K $RULE_L
		done
	done
done
