#!/bin/bash

#Name of the csv file to be generated
FILE="results.csv"

#First checks if the file exists, if not: insert row with headers
write_headers() {
	if ! [[ -f "$FILE" ]] 
	then
		col1="model_name"
		col2="query_index"
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
		echo \"$col1\",\"$col2\",\"$col3\",\"$col4\",\"$col5\",\"$col6\",\"$col7\",\"$col8\",\"$col9\",\"${col10}\",\"${col11}\",\"${col12}\",\"${col13}\",\"${col14}\",\"${col15}\",\"${col16}\",\"${col17}\",\"${col18}\",\"${col19}\",\"${col20}\",\"${col21}\" >> $FILE
	fi
}

#Takes 21 arguments, and appends a row with these argument to FILE
append_row() {
	echo \"$1\",\"$2\",\"$3\",\"$4\",\"$5\",\"$6\",\"$7\",\"$8\",\"$9\",\"${10}\",\"${11}\",\"${12}\",\"${13}\",\"${14}\",\"${15}\",\"${16}\",\"${17}\",\"${18}\",\"${19}\",\"${20}\",\"${21}\" >> $FILE
}

write_headers

# Pass data like this to function, takes 21 arguments as seen in header function, position matters when calling 
data_for_col_1="foo"
data_for_col_2="bar"
append_row "$data_for_col_1" "$data_for_col_2"
append_row "baz" "whatever-comes-after-baz"







