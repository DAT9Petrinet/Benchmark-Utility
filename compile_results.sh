#!/bin/bash

#SBATCH --time=22:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G
#SBATCH -c 4

# Args: <test-name> <binary>
# This is the last step of `run.sh`, but can also be run manually.
# This script will collect the data from all the raw output and size files belonging to the given test into a single `<binary>/<binary>/<test-name>.csv`.

NAME=$1
BIN=$(basename $2)

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
fi

if [ -z "$BIN" ] ; then
	echo "Missing binary"
	exit
fi

DIR="output/$BIN/$NAME"
OUT="output/$BIN/$NAME.csv"

# ***** Setup CSV *****

RULES=("A" "B" "C" "D" "E" "F" "G" "H" "I" "J" "K" "L" "M" "N" "O" "P" "Q" "R" "S" "T")

rm -f $OUT

# Write header
echo -n "model name,query index,time,memory,answer,solved by query simplification,prev place count,prev transition count,post place count,post transition count,reduce time,state space size," >> $OUT
for i in ${!RULES[@]} ; do
	echo -n "rule ${RULES[$i]}" >> $OUT
	if [[ $i -ne $((${#RULES[@]} - 1)) ]]; then
		echo -n "," >> $OUT
	fi
done
echo "" >> $OUT

# ***** Analysis *****

for FILE in $(ls $DIR | grep "\.out$") ; do

	echo "Collecting from $DIR/$FILE"

	# Model/query data from file name (Expected form is "ModelName.QueryIndex.out")
	MODEL=$(echo $FILE | sed -E "s/([^\.]*).*/\1/")
	Q=$(echo $FILE | sed -E "s/[^\.]*\.([0-9]*).*/\1/")

	# Get stdout of model, filter out transition and place-bound statistics, and replace new lines such that regex will work
	RES=$(cat "$DIR/$FILE" | grep -v "^<" | tr '\n' '\r')

	# Time and memory is appended to the file
	TIME=$(echo $RES | sed -E "s/.*@@@(.*),.*@@@.*/\1/")
	MEM=$(echo $RES | sed -E "s/.*@@@.*,(.*)@@@.*/\1/")

	# Did we get an answer or did the query time out?
	# We can check this by checking if "satisfied" is a substring of the output.
	# If "Query is satisfied" is also a substring, then the answer is TRUE.
	ANSWER=$([[ -n "$(echo $RES | awk '/satisfied/')" ]] && ([[ -n "$(echo $RES | awk '/Query is satisfied/')" ]] && echo "TRUE" || echo "FALSE") || echo "NONE")

	# Was query solved using query reduction?
	QUERY_SIMPLIFICATION=$([[ -n "$(echo $RES | awk '/Query solved by Query Simplification/')" ]] && echo "TRUE" || echo "FALSE")

    # Total reduction size
	PREV_PLACE_COUNT=$([[ -n "$(echo $RES | awk '/Size of net before/')" ]] && echo $RES | sed -E "s/.*Size of net before[^:]*: ([0-9]+).*/\1/" || echo 0)
	PREV_TRANS_COUNT=$([[ -n "$(echo $RES | awk '/Size of net before/')" ]] && echo $RES | sed -E "s/.*Size of net before[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)
	POST_RED_PLACE_COUNT=$([[ -n "$(echo $RES | awk '/Size of net after/')" ]] && echo $RES | sed -E "s/.*Size of net after[^:]*: ([0-9]+).*/\1/" || echo 0)
	POST_RED_TRANS_COUNT=$([[ -n "$(echo $RES | awk '/Size of net after/')" ]] && echo $RES | sed -E "s/.*Size of net after[^:]*: [0-9]+ places, ([0-9]+).*/\1/" || echo 0)

	# Reduction time
	RED_TIME=$([[ -n "$(echo $RES | awk '/Structural reduction finished after/')" ]] && echo $RES | sed -E "s/.*Structural reduction finished after (([0-9]\.[0-9]e-0[2-9])|([0-9]+(\.[0-9]+)?)) s.*/\1/" || echo 0.0)

	# Reduction state space size
	SIZE_FILE="${FILE%.*}.size"
	SIZE=$([[ -f $SIZE_FILE ]] && echo $(cat $SIZE_FILE) || echo 0)

	echo -n "$MODEL,$Q,$TIME,$MEM,$ANSWER,$QUERY_SIMPLIFICATION,$PREV_PLACE_COUNT,$PREV_TRANS_COUNT,$POST_RED_PLACE_COUNT,$POST_RED_TRANS_COUNT,$RED_TIME,$SIZE," >> $OUT

	# Applications of rules
	for i in ${!RULES[@]} ; do

		APPLICATIONS=$([[ -n "$(echo $RES | awk "/Applications of rule ${RULES[$i]}/")" ]] && echo $RES | sed -E "s/.*Applications of rule ${RULES[$i]}: ([0-9]+).*/\1/" || echo 0)

		echo -n "$APPLICATIONS" >> $OUT
		if [[ $i -ne $((${#RULES[@]} - 1)) ]]; then
			echo -n "," >> $OUT
		fi
	done
	echo "" >> $OUT
done

echo "Done"