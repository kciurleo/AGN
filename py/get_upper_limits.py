#This file takes a votable with columns 'ra' and 'dec', finds the HEALPix associated with the RA/Dec,
#queries eROSITA for the associated upper limits information, and saves the result as a new votable.
#The new table is outer joined and contains a subset of the columns the query returns.

from astropy.table import Table
import pandas as pd
import requests
from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord
from astropy.io import votable

#Parameters
infile='/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.vot'
outfile='/Users/kciurleo/Documents/kciurleo/AGN/csvs/upper_limits.vot'

#Read targets table
targets = votable.parse_single_table(infile).to_table().to_pandas()

#Get HEALPix from RA/dec
#(From the example at https://erosita.mpe.mpg.de/dr1/AllSkySurveyData_dr1/apis.html#Second_Point_Header)
hpix = HEALPix(nside=2**16, order='nested', frame='icrs')
hpidxs = hpix.skycoord_to_healpix(SkyCoord(targets['ra'], targets['dec'], unit='deg')).tolist()
targets['healpix']=hpidxs

###
# Bands of interest, with:
# 0.2-0.6 keV (soft): 021
# 0.6-2.3 keV (medium): 022
# 2.3-5.0 keV (hard): 023
# 0.2-5.0 keV (summed three-band): 02e
###

#Iterate over bands
bands = ['021', '022', '023', '02e']
all_responses=pd.DataFrame()

for band in bands:

    #Post to API to get upper limits
    url = f"https://sciserver.mpe.mpg.de/erosita-ul/ULbyHPlist/{band}/"
    req = requests.post(url, json=hpidxs)
    assert req.status_code == 200

    #Extracting only certain columns and renaming based on band
    response=pd.json_normalize(req.json()[f'{band}'])[['healpix', 'Exposure', 'Flag_pos', 'UL_B', 'UL_S']]
    response=response.rename(columns={'Exposure':f'Exposure_{band}', 'Flag_pos':f'Flag_pos_{band}', 'UL_B':f'UL_B_{band}', 'UL_S':f'UL_S_{band}'})

    #Merge all responses into all_responses
    if all_responses.empty:
        all_responses = response
    else:
        all_responses = pd.merge(all_responses, response, on='healpix', how='outer')

#Combine the response with our initial table and save as a new file
upper_limits=pd.merge(all_responses, targets, on=['healpix'],how='outer')

table = Table.from_pandas(upper_limits)
table.write(outfile, overwrite=True,format='votable')