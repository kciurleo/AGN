#This script takes in a file with a column of Chandra obsids, then checks for if they're already downloaded to a given folder
#then outputs two text files of lists of IDs

import os
import pandas as pd

#Folder to be iterated over 
folder="/Volumes/galaxies/Seth/AGNs/x-ray/new_csc/dataproducts"

#File with IDs
input_file="/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv"

#Outdirectory
out_directory = "/Users/kciurleo/Documents/kciurleo/AGN/csvs/"

#Column name of IAU object name
column_name="CHANDRA_OBSID"

#Get the IDs we're interested in
IDs=pd.read_csv(input_file, dtype={column_name: object})[column_name]

#Get the available downloads
os.chdir(folder)
downloads=os.listdir()

#Arrays for IDs we have vs. don't have
haves=[]
havenots=[]

#Iterate over IDs and sort them
for id in IDs:
    if id in downloads:
        haves.append(id)
    else:
        havenots.append(id)

#Write haves to a file
with open(out_directory+'haves.txt', 'w') as f:
    for id in haves:
        f.write(f"{id}\n")
print(f'{len(haves)} haves: {haves}')

#Remove duplicates
haves = list(set(haves))
havenots = list(set(havenots))

#Write havenots to a file
with open(out_directory+'havenots.txt', 'w') as f:
    for id in havenots:
        f.write(f"{id}\n")
print(f'{len(havenots)} havenots: {havenots}')