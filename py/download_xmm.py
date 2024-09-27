#This program downloads XMM data for a list of observation_id

import os
import numpy as np
from astropy.io import fits
import pandas as pd
from astroquery.esa.xmm_newton import XMMNewton
import glob
import tarfile

#Input file
input=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/ALL_observed_full_info.csv')

#Directory to download data into
dir="/opt/pwdata/katie/xmm"

#Move into the downloads
os.chdir(dir)

#Extract tar file definition
def extract_all_files(tar_file_path, extract_to):
    with tarfile.open(tar_file_path, 'r') as tar:
        tar.extractall(extract_to)

#probably should do the id thing of abcdefg

#Iterate over the obsids, and download only the ftz files for the correct src number
for id, row in input.head(8).iterrows():
    #needs to have 10 digits
    obsid = str(row['observation_id']).zfill(10)
    srcno=int(row['src_num'])
    print(f'Downloading {obsid} for {srcno}')

    #Download everything for the right source
    XMMNewton.download_data(obsid, level='PPS',extension='FTZ', sourceno=f"{srcno:03X}")

    #Extract files and delete
    print(f'Extracting {obsid}')
    extract_all_files(f'{obsid}.tar', '')
    os.remove(f"{obsid}.tar") 
    os.chdir(f'{dir}/{obsid}')

    #deal with bkg
    XMMNewton.download_data(obsid, filename='bkg.tar',level='PPS',extension='FTZ', name='BGSPEC')
    extract_all_files(f'bkg.tar', 'bkg')
    os.remove("bkg.tar")
    os.chdir(dir)

    #Open the correct fits header to
    print('globs:',len(glob.glob(f'{dir}/{obsid}/pps/*SRSPEC{f"{srcno:04X}"}*')))
    hdrfile=glob.glob(f'{dir}/{obsid}/pps/*SRSPEC{f"{srcno:04X}"}.FTZ')[0]
    respfile=fits.getheader(f'{hdrfile}',ext=1)['RESPFILE']
    print(fits.getheader(f'{hdrfile}',ext=1)['SRCNUM'])
    print(respfile)