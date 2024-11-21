import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import best_model
from astropy.io import fits
from astropy.time import Time
import glob
from ciao_contrib.runtool import *
from astropy import units as u
from astropy.coordinates import SkyCoord
import re

#input into the process:
input_file=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_process_input.csv')

#errors
match_error = pd.read_csv('/opt/pwdata/katie/csc2.1/matching_error.txt', skiprows=1, names=['ids', 'date', 'exp', 'theta'])
fit_error = pd.read_csv('/opt/pwdata/katie/csc2.1/fitting_error.txt', skiprows=1, names=['ids'])
wav_error = pd.read_csv('/opt/pwdata/katie/csc2.1/wavdetect_error.txt', skiprows=1, names=['ids'])

#other
stats =  pd.read_csv('/opt/pwdata/katie/csc2.1/stats.csv')
compton = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_compton_list.txt', skiprows=1, names=['ids'])
triply_unabsorbed_list = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/triply_unabsorbed_list.txt', skiprows=1, names=['ids'])

#individual fits
main = pd.read_csv('/opt/pwdata/katie/csc2.1/allinfo_full_withratio.csv')
res = pd.read_csv('/opt/pwdata/katie/csc2.1/allinfo_full_withratio_res.csv')
alt = pd.read_csv('/opt/pwdata/katie/csc2.1/allinfo_full_withratio_alt.csv')

#final lists
final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
final_min_abs = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_min_abs_full.csv')
final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')

print(input_file)

files = [file for file in os.listdir('/opt/pwdata/katie/csc2.1') if not file.startswith('._')]
total = set([entry for entry in files if os.path.isdir(f'/opt/pwdata/katie/csc2.1/{entry}')])

print(len(total))

#compton thick in all different versions
main_compton = main.loc[main['compton thick']=='True']
res_compton = res.loc[res['compton thick']=='True']
alt_compton = alt.loc[alt['compton thick']=='True']

#minabs in all different versions, comes from files because isn't explicitly done in the code. but maybe should be.
final_reps = [file for file in os.listdir('/opt/pwdata/katie/csc2.1/final_data') if not file.startswith('._')]
final_reps = set([entry for entry in final_reps if os.path.isdir(f'/opt/pwdata/katie/csc2.1/final_data/{entry}')])
main_reps = [file for file in os.listdir('/opt/pwdata/katie/csc2.1/min_abs') if not file.startswith('._')]
main_reps = set([entry for entry in main_reps if os.path.isdir(f'/opt/pwdata/katie/csc2.1/min_abs/{entry}')])
alt_reps = [file for file in os.listdir('/opt/pwdata/katie/csc2.1/min_abs_alt') if not file.startswith('._')]
alt_reps = set([entry for entry in alt_reps if os.path.isdir(f'/opt/pwdata/katie/csc2.1/min_abs_alt/{entry}')])
res_reps = [file for file in os.listdir('/opt/pwdata/katie/csc2.1/min_abs_res') if not file.startswith('._')]
res_reps = set([entry for entry in res_reps if os.path.isdir(f'/opt/pwdata/katie/csc2.1/min_abs_res/{entry}')])

#identifying guys with mismatching stats
unabsorbed=final_full.loc[final_full['unabsorbed']==True]

always_unabsorbed=[]
problem_children={}

for id, row in unabsorbed.iterrows():
    #find all the instances of this object which passed matching
    obj=row['CXO name']
    obj_df=final_full.loc[final_full['CXO name']==obj]
    
    #always unabsorbed (or ones w/only one observation) will all have the same 'True' value
    if len(set(obj_df['unabsorbed'])) == 1:
        if obj not in always_unabsorbed:
            always_unabsorbed.append(obj)
    else:
        if obj not in problem_children:
            #figure out who's the brightest and use that as the "real" one
            obsids = obj_df['# ObsID']
            max_time = 0
            brightest_obsid = ''

            for obsid in obsids:
                #obsid without letters
                obsid_num=re.sub('[a-zA-Z]', '', obsid)
                time=float(input_file.loc[input_file['CHANDRA_OBSID']==float(obsid_num)].iloc[0][' TIME'])
                
                #save the time and obsid if it's a longer exposure
                if time > max_time:
                    max_time=time
                    brightest_obsid=obsid

            #save the best one
            problem_children[obj] = brightest_obsid

#add our new "always unabs" and the corresponding brightest obsid for the not always guys
unabsorbed['always unabs'] = unabsorbed['CXO name'].isin(always_unabsorbed)
unabsorbed['brightest obsid'] = unabsorbed['CXO name'].map(problem_children)

#these two numbers should add up to the third
print(len(always_unabsorbed))
print(len(problem_children))
print(len(unabsorbed['CXO name'].unique()))

#these two numbers should add up to the third
print(len(unabsorbed.loc[unabsorbed['always unabs']==True]))
print(len(unabsorbed.loc[unabsorbed['always unabs']==False]))
print(len(unabsorbed['CXO name']))

#kick out 

#Printing stuff
print(f"Input file had {len(input_file)} obsid-object combos")
print(f"Ran code for {len(total)} obsid-object combos")
print(f"Wavdetect errors: {len(wav_error)}")
print(f"Match region errors: {len(match_error)}")
print(f"Sherpa fitting errors: {len(fit_error)}")
print()
print(f"Compton thick candidates in 'best' model: {len(compton)}")
print(f"Main Compton thick candidates: {len(main_compton)}")
print(f"Alt Compton thick candidates: {len(alt_compton)}")
print(f"Res Compton thick candidates: {len(res_compton)}")
print(f"Compton thick in at least one model: {len(set(main_compton) | set(alt_compton) | set(res_compton))}")
print()
print(f'Total "best" min abs using my current best model method: {len(final_reps)}')
print(f'Should be the same as this number: {len(unabsorbed)}')
print(f'Total main fit min abs: {len(main_reps)}')
print(f'Total alt fit min abs: {len(alt_reps)}')
print(f'Total res fit min abs: {len(res_reps)}')
print(f'Total min abs in at least one fit: {len(main_reps | alt_reps | res_reps )}')
print(f"Triply unabsorbed: {len(triply_unabsorbed_list)}")