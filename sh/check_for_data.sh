#!/bin/sh

#This script takes in a file with a column of Chandra obsids, then checks for if they're already downloaded to a given folder

#File with IDs
input_file="/Users/kciurleo/Documents/kciurleo/new_file.csv"

#Folder to search
folder="/Volumes/galaxies/Seth/AGNs/x-ray/new_csc/dataproducts"

#Column name of IAU object name
column_name="CHANDRA_OBSID"

#Get the obsid column
obsid_column=$(awk -v col="$column_name" -F ',' 'NR==1{for(i=1;i<=NF;i++) if($i==col){print i; exit}}' "$input_file")

echo "$obsid_column[$1]"