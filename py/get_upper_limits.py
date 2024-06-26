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
band = '021'

###
# Band of interest, with:
# 0.2-0.6 keV (soft): 021
# 0.6-2.3 keV (medium): 022
# 2.3-5.0 keV (hard): 023
# 0.2-5.0 keV (summed three-band): 02e
###

#Read targets table
targets = votable.parse_single_table(infile).to_table().to_pandas()

#Get HEALPix from RA/dec
#(From the example at https://erosita.mpe.mpg.de/dr1/AllSkySurveyData_dr1/apis.html#Second_Point_Header)
hpix = HEALPix(nside=2**16, order='nested', frame='icrs')
hpidxs = hpix.skycoord_to_healpix(SkyCoord(targets['ra'], targets['dec'], unit='deg')).tolist()
targets['healpix']=hpidxs

#Post to API to get upper limits
url = f"https://sciserver.mpe.mpg.de/erosita-ul/ULbyHPlist/{band}/"
req = requests.post(url, json=hpidxs)
assert req.status_code == 200

#Combine the response with our initial table and save as a new file, extracting only certain columns
response=pd.json_normalize(req.json()[f'{band}'])[['healpix', 'Exposure', 'Flag_pos', 'UL_B', 'UL_S']]
upper_limits=pd.merge(response, targets, on=['healpix'],how='outer')
table = Table.from_pandas(upper_limits)
table.write(outfile, overwrite=True,format='votable')
