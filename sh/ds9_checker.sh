#!/bin/sh

#This program iterates over the unmatched targets, opens their detect_imgfile.fits in ds9, and puts both the region 
#and a marker of where the AGN is on the image, then saves and opens a png for visual inspection. 

input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/visual_match_error.csv"


#ciao
source activate ciao-4.16

{
  read #this skips header
  count=0
  while IFS=, read -r id name obsid ra dec z nh counts date exp theta; do
    count=$((count + 1))

    if [ "$count" -le 29 ]; then
      echo "$obsid" "$ra" "$dec"
      cd "/opt/pwdata/katie/csc2.1/$obsid/primary/"
      #do all the ds9 stuff
      ds9 detect_imgfile.fits -region detect_src.reg -region command "fk5;circle $ra $dec 0.002 # color=red" -scale log -saveimage xtest.png &
      sleep 5
      pkill -f ds9
      open xtest.png
    else
      break
    fi
  done
} < "$input_file"