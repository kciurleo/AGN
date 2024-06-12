#!/bin/sh

#File with names
input_file="/Users/kciurleo/Documents/kciurleo/file.csv"
#NOTE: input csv file should have one blank line at the end, or the last line will get cut off.

#Output file
output_file="/Users/kciurleo/Documents/kciurleo/new_file.csv"

#Column names of IAU object name and new column with IDs
column_name="IAUNAME"
new_column="CHANDRA_OBSID"

#Get rid of empty rows, via temporary file
temp_file=$(mktemp)
awk 'NF > 0' "$input_file" > "$temp_file"
mv "$temp_file" "$input_file"

#Get the IAU object name column
iauname_column=$(awk -v col="$column_name" -F ',' 'NR==1{for(i=1;i<=NF;i++) if($i==col){print i; exit}}' "$input_file")

#Loop through csv file
while IFS= read -r line; do
    # Skip the first line
    if $skip_header; then
        skip_header=false
        continue
    fi
    #Get the IAU name
    iauname=$(echo "$line" | awk -F ',' -v col="$iauname_column" '{print $col}')
    #echo "$iauname"

    #Add CHANDRA_OBSID
    awk -v d="$iauname" -v col="$new_column" -F"," 'FNR==1{a=col} FNR>1{a=d} {print $0", "a}' "$input_file" > "$output_file"
done < "$input_file"

#Make sure the file gets read all the way to the end by adding a blank line
echo >> "$input_file"