#!/bin/sh

# Used for copying directory between old and new spots, given an input_file with a list of obsids
# This version accounts for the possibility that the file is in two places, and skips the copying
# if the file already exists at the end directory.

input_file="/Users/kciurleo/Documents/kciurleo/AGN/unorganized/seth_final_obsids.txt"

# Directories
start_dir1="/Volumes/galaxies/Seth/AGNs/x-ray/new_csc/dataproducts/"
start_dir2="/Volumes/galaxies/Seth/AGNs/x-ray/csc_v2/"
start_dir3="/Volumes/galaxies/Katie/xray_data/"
end_dir="/opt/katie/data/"

# Function to check if directory exists
directory_exists() {
    [ -d "$1" ]
}

# Unfound directories
unfound=()

# Copy entire directories
while read F  ; do
    if directory_exists "$end_dir$F"; then
        echo "$F already exists in $end_dir, skipping."
    else
        if directory_exists "$start_dir1$F"; then
            cp -r "$start_dir1$F" "$end_dir"
            echo "Copied $F from $start_dir1"
        elif directory_exists "$start_dir2$F"; then
            cp -r "$start_dir2$F" "$end_dir"
            echo "Copied $F from $start_dir2"
        elif directory_exists "$start_dir3$F"; then
            cp -r "$start_dir3$F" "$end_dir"
            echo "Copied $F from $start_dir3"
        else
            echo "Directory $F not found in either $start_dir1 or $start_dir2 or $start_dir3"
            unfound+=("$F")
        fi
    fi
done < "$input_file"

echo "${#unfound[@]} items not found in either directory: "
for dir in "${unfound[@]}"; do
        echo "$dir"
done