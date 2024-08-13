#!/bin/sh

#This program checks the sources which failed during wavdetect to see if their folders are empty. If so, download the obsids.

input_file="/opt/pwdata/katie/csc2.1/wavdetect_error.txt"

#lists
empty=()
unempty=()
total=0

source activate ciao-4.16

#Check if dirs are empty or not
while IFS= read -r F; do
    total+=1
    if [[ "${F%% *}" == "#This" ]]; then
        continue
    fi
        obsid="${F%% *}"
        #echo "$obsid"
        if [ -z "$( ls -A "/opt/pwdata/katie/csc2.1/$obsid/primary" )" ]; then
            #echo "$obsid Empty"
            empty+=("$obsid")
            #download_chandra_obsid "$obsid";
        else
            #echo "$obsid Not Empty"
            unempty+=("$obsid")
        fi

done < "$input_file"

echo "$total total directories."

echo "${#empty[@]} directories are empty:"
for dir in "${empty[@]}"; do
        echo "$dir"
done

echo "${#unempty[@]} directories are unempty:"
for dir in "${unmpty[@]}"; do
        echo "$dir"
done