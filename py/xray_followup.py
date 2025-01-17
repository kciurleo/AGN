#This file identifies minimally absorbed AGN which have yet to be observed by XMM.

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from ciao_contrib.runtool import *
import glob
import os
from astropy.io import fits, votable

#Other
xmm = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_4arcsec_query_result.vot').to_table().to_pandas().drop_duplicates()
input = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_process_input.csv')[['CSC21P_name', 'CHANDRA_OBSID', ' OBSDATE', ' TIME', 'MJD','PLATE','FIBERID']]
compton = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_compton_list.txt', skiprows=1, names=['ids'])
triply_unabsorbed_list = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/triply_unabsorbed_list.txt', skiprows=1, names=['ids'])

final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',engine='python',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
final_min_abs = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_min_abs_full.csv')
final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')

#merge the xmm and input tables so we can know who the XMM guys correspond to
cone_result = pd.merge(xmm, input, how='outer', on=['MJD','PLATE','FIBERID'])

#Doing everything for the triply unabsorbed list for now, since they're the most steady KATIE GO BACK AND ALSO DO OTHERS
dates=[]
exps=[]

#merge with full list so we can have all the info
triply_unabsorbed_list=pd.merge(triply_unabsorbed_list, final_full, how='left', left_on='ids', right_on='# ObsID')
triply_unabsorbed_list=pd.merge(triply_unabsorbed_list, cone_result, how='left', left_on='CXO name', right_on='CSC21P_name')
print(triply_unabsorbed_list.columns)
#gotta get rid of some duplicates when it comes to the chandra obsids being listed multiple times in input
for i, row in triply_unabsorbed_list.iterrows():
    if row['ids'][-1] in ['a','b','c','d','e','f','g']:
        id = row['ids'][:-1]
    else:
        id=row['ids']
    if int(id)!=int(row['CHANDRA_OBSID']):
        triply_unabsorbed_list=triply_unabsorbed_list.drop(i)

#rest of the duplicates should be for xmm reasons
#print(triply_unabsorbed_list[['ids','model','CXO name','RA','Dec','counts',' OBSDATE',' TIME','MJD','FIBERID','PLATE','IAUNAME','duration','ra','dec']])

unobserved_list=[]
observed_list=[]
for i, row in triply_unabsorbed_list.iterrows():
    #if nan for xmm duration, add to a list of unobserved targets
    if pd.isna(row['duration']):
        unobserved_list.append(row['ids'])
    else:
        observed_list.append(row['ids'])

#save a version of final_full with just the unobserved guys
unobserved_info_full = pd.DataFrame(columns=final_full.columns)
observed_info_full = pd.DataFrame(columns=final_full.columns)

for obsid in unobserved_list:
    temp_row_dude=final_full.loc[final_full['# ObsID']==f'{obsid}']
    unobserved_info_full = pd.concat([unobserved_info_full, temp_row_dude], ignore_index=True)

unobserved_info_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/unobserved_full_info.csv',index=False)
#print(unobserved_info_full[['# ObsID', 'unabsorbed', 'model', 'Cstat', 'nH', 'nH error plus', 'nH error minus', 'gamma', 'gamma error plus', 'gamma error minus','CXO name', 'RA', 'Dec', 'Z', 'galactic nH', 'counts','luminosity', 'luminosity error']])

#same for observed
for obsid in observed_list:
    temp_row_dude=final_full.loc[final_full['# ObsID']==f'{obsid}']
    observed_info_full = pd.concat([observed_info_full, temp_row_dude], ignore_index=True)

observed_info_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/observed_full_info.csv',index=False)
#print(observed_info_full)

print(len(unobserved_info_full['CXO name'].unique()))
print(len(observed_info_full['CXO name'].unique()))


###
# Redoing the above but for all of the min abs seyferts
###

dates=[]
exps=[]

#merge with cone list so we can have all the info

final_min_abs=pd.merge(final_min_abs, cone_result, how='left', left_on='CXO name', right_on='CSC21P_name')

#gotta get rid of some duplicates when it comes to the chandra obsids being listed multiple times in input
for i, row in final_min_abs.iterrows():
    if row['# ObsID'][-1] in ['a','b','c','d','e','f','g']:
        id = row['# ObsID'][:-1]
    else:
        id=row['# ObsID']
    if int(id)!=int(row['CHANDRA_OBSID']):
        final_min_abs=final_min_abs.drop(i)

#rest of the duplicates should be for xmm reasons
#print(final_min_abs[['# ObsID','model','CXO name','RA','Dec','counts',' OBSDATE',' TIME','MJD','FIBERID','PLATE','IAUNAME','duration','ra','dec']])

unobserved_list=[]
observed_list=[]
print(final_min_abs.columns)
for i, row in final_min_abs.iterrows():
    #if nan for xmm duration, add to a list of unobserved targets
    if pd.isna(row['duration']):
        unobserved_list.append(row['# ObsID'])
    else:
        observed_list.append(row['# ObsID'])

#save a version of final_full with just the unobserved guys
unobserved_info_full = pd.DataFrame(columns=final_min_abs.columns)
observed_info_full = pd.DataFrame(columns=final_min_abs.columns)

for obsid in unobserved_list:
    temp_row_dude=final_min_abs.loc[final_min_abs['# ObsID']==f'{obsid}']
    unobserved_info_full = pd.concat([unobserved_info_full, temp_row_dude], ignore_index=True)
    
#Make sure we're only saving the unique chandra object, XMM obsid, srcid combos
unobserved_info_full=unobserved_info_full.drop_duplicates(subset=['CXO name', 'observation_id', 'srcid'])
unobserved_info_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/ALL_unobserved_full_info.csv',index=False)
#print(unobserved_info_full[['# ObsID', 'unabsorbed', 'model', 'Cstat', 'nH', 'nH error plus', 'nH error minus', 'gamma', 'gamma error plus', 'gamma error minus','CXO name', 'RA', 'Dec', 'Z', 'galactic nH', 'counts', 'luminosity', 'luminosity error']])

#same for observed
for obsid in observed_list:
    temp_row_dude=final_min_abs.loc[final_min_abs['# ObsID']==f'{obsid}']
    observed_info_full = pd.concat([observed_info_full, temp_row_dude], ignore_index=True)

#Make sure we're only saving the unique chandra object, XMM obsid, srcid combos
observed_info_full=observed_info_full.drop_duplicates(subset=['CXO name', 'observation_id', 'srcid'])
observed_info_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/ALL_observed_full_info.csv',index=False)

print(len(unobserved_info_full['CXO name'].unique()))
print(len(observed_info_full['CXO name'].unique()))
print(len(final_min_abs['CXO name'].unique()))

#Find all the guys for which all the chandra observations are less than 100 or 300 counts
low_count_unobserved_names=[]
for i in range(len(unobserved_info_full['CXO name'].unique())):
    name=unobserved_info_full['CXO name'].unique()[i]

    df=final_full.loc[final_full['CXO name']==name]
    if (df['counts'] < 300).all():
        low_count_unobserved_names.append(name)

low_count_unobserved = final_min_abs.loc[final_min_abs['CXO name'].isin(low_count_unobserved_names)]
low_count_unobserved.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/low_count_unobserved.csv',index=False)

print(low_count_unobserved)
print(len(low_count_unobserved['CXO name'].unique()))