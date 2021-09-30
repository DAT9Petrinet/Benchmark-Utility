#!/bin/bash

# Args: <test-name>
# Collects data from test called <test-name> into a single csv. Then removes all temp files.

NAME=$1

if [ -z "$NAME" ] ; then
	echo "Missing benchmark name"
	exit
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

for FILE in $(ls output) ; do

	# Check if file name matches regex
	if [[ $FILE =~ $NAME\..*\.csv ]] ; then

		echo "Collecting from output/$FILE"

		cat "output/$FILE" >> $OUT
		# New line character
		echo "" >> $OUT

		# Remove the file
		rm "output/$FILE"

	fi
done

rm output/temp-$NAME-*
