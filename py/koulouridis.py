# This is a collection of code useful for comparing the sample of Koulouridis XMM-identified Seyferts
# to my sample.

import pandas as pd
import numpy as np
from astropy.io import votable

koulouridis = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/koulouridis_results.csv')
seyferts = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv')

print(koulouridis['Target Name'].unique())

found = pd.DataFrame(columns=seyferts.columns)
unfound = []

for id in np.array(koulouridis['Obs ID']):
    row = seyferts.loc[seyferts['CHANDRA_OBSID']==id]

    if len(row) == 0:
        unfound.append(id)
    else:
        found._append(row)

print(found)
print('unfound =',unfound)

other_koulouridis = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/koulouridis.csv')
print(other_koulouridis.columns)
xmm = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()
print(xmm.columns)

found2 = pd.DataFrame(columns=xmm.columns)
unfound2 = []

for i in range(len(np.array(other_koulouridis['Name']))):
    interest = other_koulouridis.iloc[i]
    
    row = xmm.loc[(xmm['ra_2']==interest['RA']) & (xmm['dec_2']==interest['Dec'])]

    if len(row) == 0:
        unfound2.append(interest['Name'])
    else:
        found2._append(row)

print(found2)
print('unfound =',unfound2)