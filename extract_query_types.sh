#!/bin/bash
#SBATCH --time=3:00:00
#SBATCH --mail-type=FAIL
#SBATCH --partition=rome
#SBATCH --mem=15G

# Args: [test-folder]
# Finds type (EF or AG) of reachability cardinality formulas in the given test folder and stores it as `RCtypes.csv`

TEST_FOLDER=$1

if [ -z "$TEST_FOLDER" ] ; then
	echo "No TEST_FOLDER given, using MCC2021"
	TEST_FOLDER="MCC2021"
fi

OUT="query_types/RC_types.csv"
rm -f $OUT
mkdir "query_types"
echo "model name,query index,type" >> $OUT

for MODEL in $(ls $TEST_FOLDER) ; do

	# Extract propeties. It's every 5th line offset by 4
	PROPS=$(cat "$TEST_FOLDER/$MODEL/ReachabilityCardinality.txt" | awk 'NR % 5 == 4')
	
	# Read each line in variable PROPS
	Q=1
	while IFS= read -r PROP; do
		
		# Extract and output type
		TYPE=$([[ -n $(echo $PROP | awk '/^ *E F/') ]] && echo "EF" || echo "AG")
		echo "$MODEL.$Q : $TYPE"
		echo "$MODEL,$Q,$TYPE" > $OUT

		((Q=Q+1))
	done <<< "$PROPS"
done

echo "Done"

exit 0