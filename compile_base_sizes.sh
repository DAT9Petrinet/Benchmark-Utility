#!/bin/bash

# Collects the sizes of base models to a csv called `sizes.csv`

OUT="sizes/sizes.csv"
rm -f $OUT

echo "model name,original state space size" >> $OUT

for SIZE_FILE in $(ls "sizes" | grep "\.size$") ; do

	MODEL="${FILE%%.*}"

	SIZE=$(cat "sizes/$MODEL.size")
	echo "$MODEL,$SIZE" >> $OUT

done
