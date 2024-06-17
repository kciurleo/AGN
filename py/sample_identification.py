#This file selects Seyferts out of CSC2.1, with the help of queries agostino_query.txt and portsmouth_query.txt
#and returns useful statistics on the sample

import pandas as pd
from astropy.io import votable

#Note to self: check file paths

#Read CSC 2.1 into dataframe
data=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv')

#Read in 2.0
old_data=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/oldXmatch.csv')

#Read 4XMM-DR13 into dataframe
XMM=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/4XMM_DR13cat_v1.0.csv')

#Read in SPIDERS data
SPIDERSROS = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/spidersros.xml').to_table().to_pandas()
SPIDERSXMM = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/spidersxmm.xml').to_table().to_pandas()

#Portsmouth classifications https://salims.pages.iu.edu/agn/
portsmouth=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/point_sources_classified_lines.csv')

#Agostino classifications https://salims.pages.iu.edu/agn/ and spectral IDs
agostino=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/agostino2021_table1.csv')
agostino_IDs=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/agostino_specIDs.csv')

#Rename XMM ra/dec to avoid confusion later on
XMM['XMM_ra']=XMM['ra']
XMM['XMM_dec']=XMM['dec']

#Add IAU name for easy crossmatching later
XMM['IAU_stripped']=XMM['iauname'].str[5:]

#To compare CSC2.1 to CSC2.0:
both_data = data.merge(old_data, indicator=True, how='inner', left_on='CSC21P_name', right_on='CSC2_ID')

#Find only sources with SDSS data
sources = data.dropna(subset=['Sep_SPEC_CSC21P'])

#Find only non-extended CSC sources
point_sources = sources.loc[sources['extent_flag']==False]

#Saved point sources as csv, which was used in SciServer CasJobs SQL query to get Portsmouth classifications
point_sources.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/point_sources.csv', index=False) 

#Find all XMM SPIDERS 
xspi_s2 = SPIDERSXMM.loc[(SPIDERSXMM['source_type']=="NLAGN")]

#Find all ROSAT SPIDERS which are point sources, and then which are S2
rosspi_points = SPIDERSROS.loc[(SPIDERSROS['extent_likelihood']<1)]
rosspi_s2 = rosspi_points.loc[(rosspi_points['source_type']=="NLAGN")]

#Combined SPIDERS s2
spi_s2 = pd.merge(rosspi_s2, xspi_s2, how="outer", on=['sdss_spec_plate_num', 'sdss_spec_mjd_num', 'sdss_spec_fiber_num'])

#Merge agostino IDs into normal agostino table
agostino_full =pd.merge(agostino_IDs, agostino, left_on=['objID'], right_on=['SDSS_ObjID'], how='inner')

#Combine our point source table, portsmouth classification, and agostino classifications
combined = pd.merge(point_sources, portsmouth, left_on=['PLATE', 'MJD', 'FIBERID'],right_on=['plate', 'mjd', 'fiberID'], how='left')
classified_point_sources = pd.merge(combined, agostino_full, left_on =['specobjID'],right_on=['specobjID'],how='left')

#Add IAU name to our sources
classified_point_sources['IAU_stripped']=classified_point_sources['CSC21P_name'].str[5:]

#Make full table of XMM and CSC data
full_point_sources=pd.merge(classified_point_sources,XMM,how='left', on=['IAU_stripped'])
full_point_sources.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_point_sources.csv', index=False) 

#Subset of point sources with XMM data
XMM_point_sources=full_point_sources.loc[full_point_sources['detid'] >0]

#Find only Seyfert Galaxies, classified as bpt="Seyfert" for Portsmouth and sl_class1=1 for Agostino (latter is specifically Seyfert 2s)
portsmouth_s2=full_point_sources.loc[full_point_sources['bpt']=="Seyfert"]
agostino_s2=full_point_sources.loc[full_point_sources['sl_class1']==1]

#Those classified by both
inner_s2=pd.merge(agostino_s2, portsmouth_s2, how='inner')

#Those classified by either
outer_s2=pd.merge(agostino_s2, portsmouth_s2, how='outer')
outer_s2.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv', index=False) 

#Those that are fully unclassified by both agostino and portsmouth
unclassified = full_point_sources.loc[((full_point_sources.bpt.isnull()) | (full_point_sources['bpt']=="BLANK")) & ((full_point_sources['sl_class1']==0) | (full_point_sources.sl_class1.isnull()))] 

print(f'Sources in 2.1: {len(data):,}')
print(f'Sources in 2.0: {len(old_data):,}')
print(f'Sources in both: {len(both_data):,}')
print(f'Sources from 2.0 excluded from 2.1: {len(old_data)-len(both_data):,} ')
print(f'New sources in 2.1: {len(data)-len(both_data):,}')
print()
print(f'Total observations in 2.1 crossmatch: {len(data)}')
print(f'Sources matched with SDSS: {len(sources)}, {len(data)-len(sources)} not observed with SDSS')
print(f'Point sources: {len(point_sources)}, {len(sources)-len(point_sources)} extended sources')
print(f'Unique point sources with exact XMM data: {len(XMM_point_sources["IAU_stripped"].unique())}')
print()
print(f'Unique SPIDERSROS point sources: {len(rosspi_points["name"].unique())}, {len(SPIDERSROS["name"].unique()) - len(rosspi_points["name"].unique())} sources with extent likelihood >1')
print(f'Unique SPIDERSROS NLAGN: {len(rosspi_s2["name"].unique())}, {len(rosspi_points["name"].unique())-len(rosspi_s2["name"].unique())} non-Seyfert 2s')
print(f'Unique SPIDERSXMM NLAGN: {len(xspi_s2["name"].unique())}, {len(SPIDERSXMM["name"].unique())-len(xspi_s2["name"].unique())} non-Seyfert 2s')
print(f'Total SPIDERS NLAGN: {len(spi_s2)}')
print(f"Total SPIDERS present in CSC2.1: {len(pd.merge(spi_s2, classified_point_sources, left_on=['sdss_spec_plate_num', 'sdss_spec_mjd_num', 'sdss_spec_fiber_num'], right_on=['PLATE', 'MJD', 'FIBERID'],how='inner'))}")
print()
print(f'Unique unclassifiable or non-classified sources: {len(unclassified["CSC21P_name"].unique())}')
print(f'Unique Portsmouth Seyferts: {len(portsmouth_s2["CSC21P_name"].unique())}, {len(point_sources["CSC21P_name"].unique())-len(unclassified["CSC21P_name"].unique())-len(portsmouth_s2["CSC21P_name"].unique())} classified non-Seyferts')
print(f'Unique Agostino Seyferts: {len(agostino_s2["CSC21P_name"].unique())}, {len(point_sources["CSC21P_name"].unique())-len(unclassified["CSC21P_name"].unique())-len(agostino_s2["CSC21P_name"].unique())} classified non-Seyferts')
print()
print(f'Unique Portsmouth-Agostino Seyferts: {len(inner_s2["CSC21P_name"].unique())}')
print(f'Unique Portsmouth or Agostino Seyferts: {len(outer_s2["CSC21P_name"].unique())}')
print(f"Unique Portsmouth or Agostino Seyferts processed with 2.1: {len(outer_s2.loc[outer_s2['csc2.1_flag']==True]['CSC21P_name'].unique())}, {len(outer_s2) -len(outer_s2.loc[outer_s2['csc2.1_flag']==True]['CSC21P_name'].unique())} not yet processed")
print(f'Unique Portsmouth or Agostino Seyferts with exact XMM data: {len(outer_s2["detid"].unique())}')