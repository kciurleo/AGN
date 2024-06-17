#!/bin/sh

#Used for copying directory between old and new spots, given an input_file with a list of obsids
input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/haves.txt"

#Directories
start_dir="/Volumes/galaxies/Seth/AGNs/x-ray/new_csc/dataproducts/"
end_dir="/Volumes/galaxies/Katie/xray_data"

#Copy entire directories
while read F  ; do
        cp -r "$start_dir$F" "$end_dir"
        echo "Copied $F"
done <"$input_file"