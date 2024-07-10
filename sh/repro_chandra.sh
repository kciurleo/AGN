#!/bin/sh

#This program reprocesses a large amount of Chandra data, assuming the directories for each obsid
#are all in one input directory, with a pause in between.

#Start directory where data is downloaded
input_dir="/opt/pwdata/katie/csc2.1data"

#Make sure we're in ciao
source activate ciao-4.16

#Get the list
cd "$input_dir"
list=(*)

#Reprocess all obsids in the directory
for repo in "${list[@]}"; do
    echo "Reprocessing obsid $repo"

    #Check to see if it's already been reprocessed
    if [ ! -d "$input_dir/$repo/repro" ]; then
        chandra_repro "indir=$input_dir/$repo" "outdir=$input_dir/$repo/repro"

        #Pause for 2 minutes
        echo "Pausing.";
        sleep 60;
        echo "Pausing.";
        sleep 60;
    else
        echo "$repo already reprocessed, skipping."
    fi
done