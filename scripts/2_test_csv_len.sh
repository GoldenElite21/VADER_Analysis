#!/bin/bash

# Loop over train.csv and test.csv
for file in "train.csv" "test.csv"
do
    echo "The longest title length of $file:"
    awk -F ',' '{print length($2)}' "csv/$file" | sort -rn | head -1
    echo "The longest text length of $file:"
    awk -F ',' '{print length($3)}' "csv/$file" | sort -rn | head -1
done
