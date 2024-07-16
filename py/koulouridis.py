# This is a collection of code useful for comparing the sample of Koulouridis XMM-identified Seyferts
# to my sample.

import pandas as pd

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