#!/bin/bash

# Args: <test-name> <binary>
# After running `run.sh` the results will be scattered in a number of csv files.
# This script will collect the data from all the csv files belong to the given test into a single `<test-name>.csv`.
# It will also remove the old csv files and other temporiry files generated by the test.

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

write_headers() {
	# First check if the file exists, if not: insert row with headers
	if ! [[ -f "$OUT" ]] 
	then
		col1="model name"
		col2="query index"
		col3="time"
		col4="memory"
		col5="answer"
		col6="solved by query simplification"
		col7="prev place count"
		col8="prev transition count"
		col9="post place count"
		col10="post transition count"
		col11="rule A"
		col12="rule B"
		col13="rule C"
		col14="rule D"
		col15="rule E"
		col16="rule F"
		col17="rule G"
		col18="rule H"
		col19="rule I"
		col20="rule J"
		col21="rule K"
		col22="rule L"
		echo \"$col1\",\"$col2\",\"$col3\",\"$col4\",\"$col5\",\"$col6\",\"$col7\",\"$col8\",\"$col9\",\"${col10}\",\"${col11}\",\"${col12}\",\"${col13}\",\"${col14}\",\"${col15}\",\"${col16}\",\"${col17}\",\"${col18}\",\"${col19}\",\"${col20}\",\"${col21}\",\"${col22}\" >> $OUT
	fi
}

write_headers

for FILE in $(ls "$DIR") ; do

	echo "Collecting from $DIR/$FILE"

	cat "$DIR/$FILE" >> $OUT

	# Remove the file
	rm "$DIR/$FILE"

done

rm $DIR/*.temp
