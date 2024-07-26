#!/bin/sh

#This program reprocesses a large amount of Chandra data, assuming the directories for each obsid
#are all in one input directory, with a pause in between.

#Start directory where data is downloaded
#input_dir="/opt/pwdata/katie/csc2.1"
input_dir="/Users/kciurleo/Documents/kciurleo/temporary_variable_run"

#Make sure we're in ciao
source activate ciao-4.16

#Get the list
cd "$input_dir"
#list=(*)
list=(11735)

#Reprocess all obsids in the directory
for repo in "${list[@]}"; do
    echo "Reprocessing obsid $repo"

    #Check to see if it's already been reprocessed
    if [ ! -d "$input_dir/$repo/repro" ]; then
        chandra_repro "indir=$input_dir/$repo" "outdir=$input_dir/$repo/repro" "verbose=2" "clobber=yes"

        #Pause for 1 minute
        echo "Pausing.";
        #sleep 30;
        echo "Pausing.";
        #sleep 30;
    else
        echo "$repo already reprocessed, skipping."
    fi
done