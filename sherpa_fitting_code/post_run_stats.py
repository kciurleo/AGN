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
other_problem_children={}

print(unabsorbed.columns)
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
        
        #do the same thing with luminosity error
        if obj not in other_problem_children:
            obsids = obj_df['# ObsID']
            min_error = np.inf
            precisist_obsid = ''

            for obsid in obsids:
                #get luminosity error
                try:
                    error=float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['luminosity error'])
                except:
                    error=np.nan
                #save the lum error if it's lower
                if error < min_error:
                    min_error=error
                    precisist_obsid=obsid

            #save the best one
            other_problem_children[obj] = precisist_obsid


#add our new "always unabs" and the corresponding brightest obsid for the not always guys
unabsorbed['always unabs'] = unabsorbed['CXO name'].isin(always_unabsorbed)
unabsorbed['brightest obsid'] = unabsorbed['CXO name'].map(problem_children)
unabsorbed['precisist obsid'] = unabsorbed['CXO name'].map(other_problem_children)

#note: the brightest and precisist are often the same but not always

#these two numbers should add up to the first
print()
print()
print(len(unabsorbed['CXO name'].unique()), ' unique min abs guys')
print(len(always_unabsorbed), ' unique always unabsorbed (barring match errors)')
print(len(problem_children), ' unique not always unabsorbed')

#these two numbers should add up to the third (ununique)
'''
print(len(unabsorbed.loc[unabsorbed['always unabs']==True]))
print(len(unabsorbed.loc[unabsorbed['always unabs']==False]))
print(len(unabsorbed['CXO name']))
'''

#Make a new unabsorbed df which kicks out all the guys whose brightest obsids are NOT also min abs
imposters=[]
well_fine=[]
brightest_stars=[]
unique_imposters=[]
unique_well_fine=[]
unique_brightest_stars=[]
for id, row in unabsorbed.iterrows():
    #only care about Not always unabsorbed guys
    obsids = set(unabsorbed['# ObsID'])

    if row['always unabs']==False:
        brightest=row['brightest obsid']
        obsid=row['# ObsID']
        name=row['CXO name']
        if obsid == brightest:
            brightest_stars.append(obsid)
            unique_brightest_stars.append(name)
        elif obsid != brightest and brightest in obsids:
            well_fine.append(obsid)
            #There's some overlap in object names,so:
        elif obsid != brightest and brightest not in obsids:
            imposters.append(obsid)
            unique_imposters.append(name)

sloppy=[]
well_okay=[]
precisist_stars=[]
unique_sloppy=[]
unique_well_okay=[]
unique_precisist_stars=[]
for id, row in unabsorbed.iterrows():
    #only care about Not always unabsorbed guys
    obsids = set(unabsorbed['# ObsID'])

    if row['always unabs']==False:
        precisist=row['precisist obsid']
        obsid=row['# ObsID']
        name=row['CXO name']
        if obsid == precisist:
            precisist_stars.append(obsid)
            unique_precisist_stars.append(name)
        elif obsid != precisist and precisist in obsids:
            well_okay.append(obsid)
            #There's some overlap in object names,so:
        elif obsid != precisist and precisist not in obsids:
            sloppy.append(obsid)
            unique_sloppy.append(name)

#save a df here

print()
print(len(set(imposters)), 'obsid-obj imposters (not brightest, brightest isnt min abs)')
print(len(set(well_fine)), 'obsid-obj which arent the brightest but brightest Is min abs')
print(len(set(brightest_stars)), 'obsid-obj who are the brightest and also min abs')
print()
print(len(set(unique_imposters)), 'unique objects imposters (not brightest, brightest isnt min abs)')
print(len(set(unique_brightest_stars)), 'unique objects whose brightest obsid is min abs')
print()
print()
print('lum error version') 
print(len(set(sloppy)), 'obsid-obj imposters (not precisist, precisist isnt min abs)')
print(len(set(well_okay)), 'obsid-obj which arent the precisist but precisist Is min abs')
print(len(set(precisist_stars)), 'obsid-obj who are the precisist and also min abs')
print()
print(len(set(unique_sloppy)), 'unique objects imposters (not precisist, precisist isnt min abs)')
print(len(set(unique_precisist_stars)), 'unique objects whose precisist obsid is min abs')
print()
print()

#do some absorbed calcs
absorbed_num=len(total)-(len(wav_error)+len(match_error)+len(fit_error))-len(compton)-len(final_reps)
absorbed=final_full.loc[final_full['unabsorbed']==False]

#Printing stuff
print(f"Input file had {len(input_file)} obsid-object combos")
print(f"Ran code for {len(total)} obsid-object combos")
print(f"Wavdetect errors: {len(wav_error)}")
print(f"Match region errors: {len(match_error)}")
print(f"Sherpa fitting errors: {len(fit_error)}")
print()
print(f"Total absorbed: {absorbed_num}, using all my file method.")
print(f"Total absorbed, using False in the final_full (should be same as above): {len(absorbed)}")
print(f"Compton thick candidates in 'best' model: {len(compton)}")
print(f"Main Compton thick candidates: {len(main_compton)}")
print(f"Alt Compton thick candidates: {len(alt_compton)}")
print(f"Res Compton thick candidates: {len(res_compton)}")
print(f"Compton thick in at least one model: {len(set(main_compton) | set(alt_compton) | set(res_compton))}")
print()
print(f'Total "best" min abs using my current best model method: {len(final_reps)}')
print(f'Should be the same as this number: {len(unabsorbed)}')
print(f'Unique guys: {len(unabsorbed["CXO name"].unique())}')
print(f'Total main fit min abs: {len(main_reps)}')
print(f'Total alt fit min abs: {len(alt_reps)}')
print(f'Total res fit min abs: {len(res_reps)}')
print(f'Total min abs in at least one fit: {len(main_reps | alt_reps | res_reps )}')
print(f"Triply unabsorbed: {len(triply_unabsorbed_list)}")

#bar plot of the overall run
#at some point make this a twin axis of "unique obsids on the right axis"
plt.figure(figsize=(10,8))
labels=['Total', 'Error', 'Absorbed', 'Compton Thick', 'Minimally Absorbed']
values=[len(total), len(wav_error)+len(match_error)+len(fit_error),len(absorbed), len(compton), len(final_reps)]

plt.bar(labels, values, color ='maroon', width = 0.4, label='Total')

plt.xlabel("Full run")
plt.ylabel("Obj-Obsid combo")
plt.legend()
plt.show()

#bar plot of fits or something?


### HOW TO CHOOSE WHICH OBSID TO BELIEVE
plt.figure(figsize=(10,8))
labels=['Total "min" abs', 'Always absorbed', 'Keepers','Imposters']
values=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(unique_brightest_stars)), len(set(unique_imposters))]
values2=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(unique_precisist_stars)), len(set(unique_sloppy))]
colors=['r','g','b','purple']
width=0.35
x_base = np.arange(len(labels))

# Plot the first group of bars
plt.bar(x_base - width/2, values, color=colors, width=width, label='Longest Exposure Time')

# Plot the second group of bars
plt.bar(x_base + width/2, values2, color=colors, alpha=0.7, width=width, label='Smallest Luminosity Error')

# Add labels, legend, and grid
plt.xticks(x_base, labels)
plt.ylabel("Unique Objects")
plt.legend()
plt.show()