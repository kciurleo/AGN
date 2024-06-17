#!/bin/sh

#This script takes in a file with a column of IAU names, then finds the chandra OBSIDs (and dates and lengths/times)
#and returns a new file with added columns for the above and a row for each unique OBSID (so targets may have multiple rows)

#If there's an error with finding the obsid, return NaN values for the relevant new columns.

#File with names
input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv"

#Output file
output_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv"

#Column name of IAU object name
column_name="IAU_stripped"

#Columns to add
new_columns="CHANDRA_OBSID, OBSDATE, TIME"

#Write column headers to output file
echo "$(head -n 1 "$input_file"),$new_columns" > "$output_file"

#Get rid of empty rows, via temporary file
temp_file=$(mktemp)
awk 'NF > 0' "$input_file" > "$temp_file"
mv "$temp_file" "$input_file"

#Make sure we're in ciao
source activate ciao-4.16

#Get the IAU object name column
iauname_column=$(awk -v col="$column_name" -F ',' 'NR==1{for(i=1;i<=NF;i++) if($i==col){print i; exit}}' "$input_file")

#Loop through csv file
while IFS= read -r line; do
    #Skip the first line
    if $skip_header; then
        skip_header=false
        continue
    fi

    #Get the row's IAU name
    iauname=$(echo "$line" | awk -F ',' -v col="$iauname_column" '{print $col}')
    
    echo "Finding Chandra obsid for: $iauname"

    #Find chandra obsids
    obsid_data=$(find_chandra_obsid "$iauname")

    #Check if find_chandra_obsid had an error
    if [ $? -ne 0 ]; then
        #Add NaN values and continue
        new_line="$line,NaN,NaN,NaN"
        echo "$new_line" >> "$output_file"
        continue
    fi

    #Skip the header line in obsid_data
    obsid_data=$(echo "$obsid_data" | tail -n +2)

    #Extract obsid, obsdate, and time/length of observation
    obsids=($(echo "$obsid_data" | awk '{print $1}'))
    obsdates=($(echo "$obsid_data" | awk '{print $6}'))
    times=($(echo "$obsid_data" | awk '{print $5}'))

    echo "Found ${#obsids[@]} obsids"

    #Add new columns and values to the current line
    for ((i = 0; i < ${#obsids[@]}; i++)); do
        new_line="$line,${obsids[i]},${obsdates[i]},${times[i]}"

        #Append the new line to the output file
        echo "$new_line" >> "$output_file"
    done

done < "$input_file"

#Make sure the file gets read all the way to the end by adding an empty row
echo >> "$input_file"