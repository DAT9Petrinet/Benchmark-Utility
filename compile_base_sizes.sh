#!/bin/bash

# Collects the sizes of base models to a csv called `sizes.csv`

OUT="sizes/sizes.csv"
rm -f $OUT

echo "model,size" >> $OUT

for MODEL in $(ls "sizes" | grep "\.size$") ; do

	SIZE=$(cat $SIZE_FILE)
	echo "$MODEL,$SIZE" >> $OUT

done