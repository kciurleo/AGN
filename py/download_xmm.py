#This program downloads XMM data for a list of observation_id

import os
from astropy.io import fits
import pandas as pd
from astroquery.esa.xmm_newton import XMMNewton
from sherpa.astro.ui import *
import glob
import tarfile
import requests
from astropy.coordinates import SkyCoord
import astropy.units as u

#Input file
input=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/ALL_observed_full_info.csv')

#Directory to download data into
dir="/opt/pwdata/katie/xmm"

#Dict needed for canned rmf
sasvers_dict = {
    '5.2.0': '2001-12-19_sas5.2.0/',
    '5.4.0': '2003-01-28_sas_5.4.0/',
    '6.0.0': '2004-07-30_sas6.0.0/',
    '6.1.0': '2004-12-03_sas6.1.0/',
    '6.5.0': '2005-12-14_sas6.5.0/',
    '7.1.0': '2007-07-17_sas7.1.0/',
    '8.0.0': '2008-07-23_sas8.0.0/',
    '9.0.0': '2009-06-15_sas9.0.0/',
    '10.0.0': '2010-04-23_sas10.0.0/',
    '11.0.0': '2011-02-23_sas11.0.0/',
    '12.0.1': '2012-06-25_sas12.0.1/',
    '13.0.0': '2013-05-01_sas13.0.0/',
    '13.5.0': '2013-12-09_sas13.5.0/',
    '14.0.0': '2014-11-13_sas14.0.0/',
    '15.0.0': '2016-02-01_sas15.0.0/',
    '16.0.0': '2017-01-12_sas16.0.0/',
    '17.0.0': '2018-06-22_sas17.0.0/',
    '18.0.0': '2019-07-31_sas18.0.0/',
    '19.0.0': '2020-10-28_sas19.0.0/',
    '20.0.0': '2021-12-09_sas20.0.0/'
}

#Extract tar file definition
def extract_all_files(tar_file_path, extract_to):
    with tarfile.open(tar_file_path, 'r') as tar:
        tar.extractall(extract_to)

#Find matching source
def match_sourceno(obsid, ra, dec):
    '''
    For a given directory and an ra and dec point, sort through the directory
    to find the source that's the closest. Return the source number and main file.
    '''

    #look at all the source spectra
    filelist = glob.glob(f'{obsid}/pps/*SRSPEC*')
    print(f'matching {obsid}')
    
    #get all the ras/decs
    ras=[]
    decs=[]
    for file in filelist:
        ras.append(fits.getheader(file,ext=1)['SRC_RA'])
        decs.append(fits.getheader(file,ext=1)['SRC_DEC'])

    #get min separation with astropy coords
    point = SkyCoord(ra=ra * u.degree, dec=dec * u.degree, frame='icrs')
    coords = SkyCoord(ra=ras * u.degree, dec=decs * u.degree, frame='icrs')
    separations = point.separation(coords)
    min_index = separations.argmin()
    min_sep = separations[min_index]

    #look at the file at that index and get just the numbers trailing SRSPEC, minus the .FTZ ending
    sourceno=filelist[min_index].split('SRSPEC')[1][:-4]
    print('sourceno: ',sourceno)

    return(sourceno, filelist[min_index], min_sep)

###
#Full Code Start
###

#Move into the downloads
os.chdir(dir)

#Unlike with the chandra obsids, there's not a lot of overlap to need to do the alphabet thing for duplicates;
#only one guy, which we'll just skip and do manually at the end for now.
skiplist=[203280201]

#Lists for our iteration
badlist=[]
badsrcnolist=[]
badrmflist=[]

#Iterate over the obsids, and download all ftz files
for id, row in input.head(25).iterrows():
    #skip the skiplist guy(s) for now:
    if row['observation_id'] in skiplist:
        continue

    #needs to have 10 digits
    obsid = str(row['observation_id']).zfill(10)
    print(f'Downloading {obsid}')

    #Download everything
    try:
        #Don't download it if it's already there
        if not os.path.exists(f'{dir}/{obsid}'):
            XMMNewton.download_data(obsid, level='PPS', extension='FTZ')

            #Extract files and delete the big tar
            print(f'Extracting {obsid}')
            extract_all_files(f'{obsid}.tar', '')
            os.remove(f"{obsid}.tar") 
        else:
            print(f'Directory {obsid} already exists. Skipping download.')
    except:
        print(f'ERROR downloading {obsid}.')
        badlist.append(obsid)
        continue
    
    #Match the source to its proper XMM detected source
    try:
        src_num, main_file, min_sep = match_sourceno(obsid, row['ra'], row['dec'])
    except:
        print(f'ERROR matching {obsid}.')
        badsrcnolist.append(obsid)
        continue

    #Open the correct fits header to see what the response file is
    respfile=fits.getheader(f'{dir}/{main_file}',ext=1)['RESPFILE']

    #try to request new url, if fails (aka not status 200), request old one
    url = f'https://sasdev-xmm.esac.esa.int/pub/ccf/constituents/extras/responses/PN/{respfile}'
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        with open(f'{dir}/{obsid}/pps/{respfile}', 'wb') as file:
            file.write(response.content)
        print("File downloaded successfully from new PN")
    else:
        print('Failed to download rmf from new PN, trying old PN')
        sasvers = fits.getheader(main_file, ext=0)['SASVERS'].split('-')[1]
        url = f'https://sasdev-xmm.esac.esa.int/pub/ccf/constituents/extras/responses/old/pn/{sasvers_dict[sasvers]}{respfile.split(".")[0]}_v{sasvers[:-2]}.rmf'
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(f'{dir}/{obsid}/pps/{respfile}', 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully from old PN")
        else:
            badrmflist.append(url)
            print("Couldn't find rmf.")

    #KATIE HERE'S WHERE YOU DELETE EXTRA FILES
    #savelist: anything with.rmf, anything with the src_num string in it

    #KATIE you should also save these "minimum separations" somewhere, let's remember that

    #delete this later, this is just for fun to check it's actually working
    clean()
    load_pha(main_file)

print(f'Bad list is {len(badlist)} items.')
print(f'Bad srcno list is {len(badsrcnolist)} items.')
print(f'Bad rmf list is {len(badrmflist)} items.')
print()
print(badlist)
print(badsrcnolist)
print(badrmflist)