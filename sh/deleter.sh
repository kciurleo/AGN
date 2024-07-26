#!/bin/sh

# Used for deleting and then redownloading all the data I stole from Seth, to avoid having to repro data.
input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/haves.txt"
data_dir="/opt/pwdata/katie/csc2.1"

# Loop over each line in haves.txt
while IFS= read -r repo; do

    #Delete
    echo "Deleting repository: $repo"
    rm -r "$data_dir/$repo"

done < "$input_file"