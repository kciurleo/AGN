#!/bin/sh

#This program iterates over the unmatched targets, opens their evt2 in ds9, 

input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/visual_match_error.csv"


#ciao
source activate ciao-4.16

{
  read #this skips header
  count=0
  while IFS=, read -r id name obsid ra dec z nh counts date exp theta; do
    count=$((count + 1))

    if [ "$count" -le 7 ]; then
      echo "$obsid" "$ra" "$dec"
      cd "/opt/pwdata/katie/csc2.1/$obsid/primary/"

      # Find the file containing "evt2" in its name
      evt2_file=$(ls *evt2* 2>/dev/null | head -n 1)

      dmcopy "$evt2_file[energy=300:8000]" filtered_evt2.fits
 
      #do all the ds9 stuff
      ds9 filtered_evt2.fits -region detect_src.reg -region command "fk5;circle $ra $dec 0.002 # color=red" -scale log -bin factor 16 -zoom fit -saveimage xtest_filtered.png &
      sleep 5
      open xtest_filtered.png
    else
      break
    fi
  done
} < "$input_file"