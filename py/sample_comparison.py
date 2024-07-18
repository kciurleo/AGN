# This is a collection of code useful for comparing the sample of Koulouridis XMM-identified Seyferts
# and SPIDERS Seyferts to my sample.

import pandas as pd
import numpy as np
from astropy.io import votable

#Seyferts from my sample, my XMM cone search, and all seyferts in Koulouridis
seyferts = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv')
xmm = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()
other_koulouridis = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/koulouridis.csv')

#ChaSer results
koulouridis = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/koulouridis_results.csv')
spidersxmm = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/spidersxmm_results.csv')
spidersros = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/spidersrosat_results.csv')

#Which obsids in koulouridis cone search are present in my sample?
print(koulouridis['Target Name'].unique())

found = pd.DataFrame(columns=seyferts.columns)
unfound = []

for id in np.array(koulouridis['Obs ID']):
    row = seyferts.loc[seyferts['CHANDRA_OBSID']==id]

    if len(row) == 0:
        unfound.append(id)
    else:
        found._append(row)
print('Koulouridis by Chandra OBSID')
print(found)
print('unfound =',unfound)

#Which XMM observations in koulouridis are present in my XMM cone search?
found2 = pd.DataFrame(columns=xmm.columns)
unfound2 = []

for i in range(len(np.array(other_koulouridis['Name']))):
    interest = other_koulouridis.iloc[i]
    
    row = xmm.loc[(xmm['ra_2']==interest['RA']) & (xmm['dec_2']==interest['Dec'])]

    if len(row) == 0:
        unfound2.append(interest['Name'])
    else:
        found2._append(row)
print('Koulouridis by XMM observation')
print(found2)
print('unfound =',unfound2)

#Which obsids in spiders xmm are present in my sample?
print(spidersxmm['Target Name'].unique())

found3 = pd.DataFrame(columns=seyferts.columns)
unfound3 = []

for id in np.array(spidersxmm['Obs ID']):
    row = seyferts.loc[seyferts['CHANDRA_OBSID']==id]

    if len(row) == 0:
        unfound3.append(id)
    else:
        found3._append(row)
print('SPIDERSXMM by Chandra OBSID')
print(found3)
print('unfound =',unfound3)

#Which obsids in spiders rosat are present in my sample?
print(spidersros['Target Name'].unique())

found4 = pd.DataFrame(columns=seyferts.columns)
unfound4 = []

for id in np.array(spidersros['Obs ID']):
    row = seyferts.loc[seyferts['CHANDRA_OBSID']==id]

    if len(row) == 0:
        unfound4.append(id)
    else:
        found4._append(row)
print('SPIDERSROS by Chandra OBSID')
print(found4)
print('unfound =',unfound4)