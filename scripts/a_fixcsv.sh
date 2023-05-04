#!/bin/bash

# Define the list of files to check
files=("csv/test.csv" "csv/train.csv")

# Loop over each file and check/add header row
for file in "${files[@]}"; do
  if [[ $(head -n 1 "$file") != "\"rating\""* ]]; then
    sed -i '1s/^/"rating","title","text"\n/' "$file"
  fi
done
