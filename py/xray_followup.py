#This file identifies minimally absorbed AGN which have yet to be observed by XMM.

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from ciao_contrib.runtool import *
import glob
import os
from astropy.io import fits, votable

#Other
xmm = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas().drop_duplicates()
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
for i, row in triply_unabsorbed_list.iterrows():
    #if nan for xmm duration, add to a list of unobserved targets
    if pd.isna(row['duration']):
        unobserved_list.append(row['ids'])

#save a version of final_full with just the unobserved guys
unobserved_info_full = pd.DataFrame(columns=final_full.columns)

for obsid in unobserved_list:
    temp_row_dude=final_full.loc[final_full['# ObsID']==f'{obsid}']
    unobserved_info_full = pd.concat([unobserved_info_full, temp_row_dude], ignore_index=True)

unobserved_info_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/unobserved_full_info.csv',index=False)