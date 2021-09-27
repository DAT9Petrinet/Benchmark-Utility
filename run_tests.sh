#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --mail-user=$(whoami)
#SBATCH --mail-type=FAIL
#SBATCH --partition=naples
#SBATCH --mem=15G

NAME=$1
OPTIONS=$2
TIMING="$3"
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
	echo "No timing given, using 1 minute"
	T=1
fi


for TEST_TYPE in Reachability{Cardinality} ; do
	for MODEL in $(ls $TEST_FOLDER) ; do
		
		echo "Running $MODEL"
		
		# Find the number of queries for this model by counting how many times "<property>" appears
		NQ=$(grep "<property>" "$TEST_FOLDER/$MODEL/$TEST_TYPE.xml" | wc -l)

		for Q in $(seq 1 $NQ ) ; do
			
			echo "	Q$Q"
			CMD = "./binaries/verifypn-linux64 $OPTIONS -x $Q $TEST_FOLDER/$MODEL/model.pnml $TEST_FOLDER/$MODEL/$TEST_TYPE.xml"
			
			res=$(eval "timeout ${TIMING}m $CMD")

			# TODO Read statistics of 'res' and output to csv
		done
	done
done
