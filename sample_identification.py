import pandas as pd

#Read CSC 2.1 into dataframe
filename='/Users/kciurleo/Documents/kciurleo/AGN/unorganized/CSC2.1p_OIR_SDSSspecmatch.csv'
data=pd.read_csv(filename)
columns = data.columns

#Find only sources with SDSS data
sources = data.dropna(subset=['Sep_SPEC_CSC21P'])

#Find only non-extended CSC sources
point_sources = sources.loc[sources['extent_flag']==False]

#Saved point sources as csv, which was used in SciServer CasJobs SQL query to get Portsmouth classifications
point_sources.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/unorganized/point_sources.csv', index=False) 

#Portsmouth classifications https://salims.pages.iu.edu/agn/
portsmouth=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/unorganized/point_source_classifications.csv')

#Agostino classifications https://salims.pages.iu.edu/agn/
agostino=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/unorganized/agostino2021_table1.csv')

#Get the agostino spectral ids and merge into normal agostino table
agostino_IDs=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/unorganized/agostino_specIDs.csv')
agostino_full =pd.merge(agostino_IDs, agostino, left_on=['objID'], right_on=['SDSS_ObjID'], how='inner')

#Combine our point source table, portsmouth classification, and agostine classifications
combined = pd.merge(point_sources, portsmouth, left_on=['PLATE', 'MJD', 'FIBERID'],right_on=['plate', 'mjd', 'fiberID'], how='left')
classified_point_sources = pd.merge(combined, agostino_full, left_on =['specobjID'],right_on=['specobjID'],how='left')

#Find only Seyfert Galaxies, classified as bpt="Seyfert" for Portsmouth and sl_class1=1 for Agostino
portsmouth_s2=classified_point_sources.loc[classified_point_sources['bpt']=="Seyfert"]
agostino_s2=classified_point_sources.loc[classified_point_sources['sl_class1']==1]

#Those classified by both
inner_s2=pd.merge(agostino_s2, portsmouth_s2, how='inner')

#Those classified by either
outer_s2=pd.merge(agostino_s2, portsmouth_s2, how='outer')

print(f'Total observations in crossmatch: {len(data)}')
print(f'All source count: {len(sources)}, {len(data)-len(sources)} not observed with SDSS')
print(f'Point source count: {len(point_sources)}, {len(sources)-len(point_sources)} extended sources')
print()
print(f'Portsmouth Seyferts:{len(portsmouth_s2)}, {len(point_sources)-len(portsmouth_s2)} non-Seyferts')
print(f'Agostino Seyferts: {len(agostino_s2)}, {len(point_sources)-len(agostino_s2)} non-Seyferts')
print()
print(f'Portsmouth-Agostino Seyferts: {len(inner_s2)}')
print(f'Portsmouth or Agostino Seyferts: {len(outer_s2)}')
print()
print(f'Marginal likelihood Portsmouth AGN: {len(portsmouth_s2.loc[portsmouth_s2["likelihood_class"]=="MARGINAL"])}')
print(f'Marginal likelihood Agostino AGN: {len(agostino_s2.loc[agostino_s2["likelihood_class"]=="MARGINAL"])}')