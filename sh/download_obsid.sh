#!/bin/sh

#This program downloads data for a list of Chandra obsids, given a file with obsids and start/finish indices 
#in the run sh command (e.g. bash /Users/kciurleo/Documents/kciurleo/AGN/sh/download_obsid.sh 3 7 downloads
#lines 3 to 7) with a 5m wait in between

#File with obsids listed
#input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/havenots.txt"
input_file="/Users/kciurleo/Downloads/downloadtoopt.txt"

#End directory to download data into
cd "/opt/pwdata/katie/csc2.1data"

#Make sure we're in ciao
source activate ciao-4.16

#Get the start/finish arguments
start_id=$1
end_id=$2

#Check if line is between start and end indices, then print it
current_line=1
while IFS= read -r F; do
    if [ "$current_line" -ge "$start_id" ] && [ "$current_line" -le "$end_id" ]; then
        download_chandra_obsid "$F";
        echo "Downloaded Chandra obsid for: $F";
        #If already downloaded, Chandra doesn't redownload

        #Pause for 5 minutes
        #sleep 150;
        echo "Pausing";
        #sleep 150;
    fi
    ((current_line++))
done < "$input_file"