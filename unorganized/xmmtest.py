import pandas as pd
from astropy.io import votable
from astropy.table import Table
import matplotlib.pyplot as plt
'''
XMM_result = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()
XMM_result.rename(columns={'ra_2':'cscra', 'dec_2':'cscdec'}, inplace=True)
final=XMM_result.drop_duplicates()

final.to_csv('/Users/kciurleo/Downloads/XMMforcasjobs.csv', index=False)
'''

#All matches within 15 arcsec
falseprobtest = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/falsematchtest.csv')

#Get rid of any duplicates with the exact same spectral target objID
false_uniques=falseprobtest[falseprobtest['targetObjID'] == 0]._append(falseprobtest[falseprobtest['targetObjID'] != 0].drop_duplicates(subset=['targetObjID']))

#Now get rid of anything that has the exat same ras and decs but Would have different specobjids
final=false_uniques.drop_duplicates(subset=['specObjAll_dec','specObjAll_ra', 'ra','dec'])

#Figure out how many obj there are for each ra and dec
duplicate_counts = final.groupby(['ra', 'dec']).size().reset_index(name='num_count')
final = pd.merge(final, duplicate_counts, on=['ra', 'dec'], how='left')

ones=final.loc[final['num_count']==1]
twos=final.loc[final['num_count']==2]
threes=final.loc[final['num_count']==3]

print(f"Number of XMM objects: {len(final.drop_duplicates(subset=['ra','dec']))}")
print(f"Number of XMM objects with 1 unique SDSS within 15 arcsec: {len(ones['ra'])}")
print(f"Number of XMM objects with 2 unique SDSS within 15 arcsec: {len(twos['ra'])/2}")
print(f"Number of XMM objects with 3 unique SDSS within 15 arcsec: {len(threes['ra'])/3}")
print(f"{(15+2)/290*100:.2e} percent are problem children")