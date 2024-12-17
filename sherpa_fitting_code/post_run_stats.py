import numpy as np
import pandas as pd
from upsetplot import from_contents
import matplotlib.pyplot as plt
import upsetplot as usp
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
other_other_problem_children={}
MINother_other_problem_children={}
gamma_problem_children={}

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

        #and with fx error
        if obj not in other_other_problem_children:
            obsids = obj_df['# ObsID']
            min_error = np.inf
            precisist_obsid = ''

            for obsid in obsids:
                #get luminosity error
                try:
                    #take the worst error
                    errors=np.max([float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['flux210 error plus']),float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['flux210 error minus'])])
                except: 
                    errors=np.nan
                #save the lum error if it's lower
                if errors < min_error:
                    min_error=errors
                    precisist_obsid=obsid

            #save the best one
            other_other_problem_children[obj] = precisist_obsid

        #and with min fx error
        if obj not in MINother_other_problem_children:
            obsids = obj_df['# ObsID']
            min_error = np.inf
            precisist_obsid = ''

            for obsid in obsids:
                #get luminosity error
                try:
                    #take the best error
                    error=np.min([float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['flux210 error plus']),float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['flux210 error minus'])])
                except: 
                    error=np.nan
                #save the lum error if it's lower
                if error < min_error:
                    min_error=error
                    precisist_obsid=obsid

            #save the best one
            MINother_other_problem_children[obj] = precisist_obsid

        #and with gamma error
        if obj not in gamma_problem_children:
            obsids = obj_df['# ObsID']
            min_error = np.inf
            precisist_obsid = ''

            for obsid in obsids:
                #get luminosity error
                try:
                    #take the worst error
                    error=np.max([float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['gamma error plus']),float(final_full.loc[final_full['# ObsID']==obsid].iloc[0]['gamma error minus'])])
                except: 
                    error=np.nan
                #save the lum error if it's lower
                if error < min_error:
                    min_error=errors
                    precisist_obsid=obsid

            #save the best one
            gamma_problem_children[obj] = precisist_obsid


#add our new "always unabs" and the corresponding brightest obsid for the not always guys
unabsorbed['always unabs'] = unabsorbed['CXO name'].isin(always_unabsorbed)
unabsorbed['brightest obsid'] = unabsorbed['CXO name'].map(problem_children)
unabsorbed['precisist obsid'] = unabsorbed['CXO name'].map(other_problem_children)
unabsorbed['precisist obsid fx'] = unabsorbed['CXO name'].map(other_other_problem_children)
unabsorbed['precisist obsid fx (MIN)'] = unabsorbed['CXO name'].map(MINother_other_problem_children)
unabsorbed['precisist obsid gamma'] = unabsorbed['CXO name'].map(gamma_problem_children)

#note: the brightest and precisist are often the same but not always
#note2: fx error is a proxy for fx/oiii ratio error, since each obsid of the same obj
#should have the same error in oiii

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

bad=[]
precisist_fx_stars=[]
unique_bad=[]
unique_precisist_fx_stars=[]
for id, row in unabsorbed.iterrows():
    #only care about Not always unabsorbed guys
    obsids = set(unabsorbed['# ObsID'])

    if row['always unabs']==False:
        precisist=row['precisist obsid fx']
        obsid=row['# ObsID']
        name=row['CXO name']
        if obsid == precisist:
            precisist_fx_stars.append(obsid)
            unique_precisist_fx_stars.append(name)
        elif obsid != precisist and precisist not in obsids:
            bad.append(obsid)
            unique_bad.append(name)

MINbad=[]
MINprecisist_fx_stars=[]
MINunique_bad=[]
MINunique_precisist_fx_stars=[]
for id, row in unabsorbed.iterrows():
    #only care about Not always unabsorbed guys
    obsids = set(unabsorbed['# ObsID'])

    if row['always unabs']==False:
        precisist=row['precisist obsid fx (MIN)']
        obsid=row['# ObsID']
        name=row['CXO name']
        if obsid == precisist:
            MINprecisist_fx_stars.append(obsid)
            MINunique_precisist_fx_stars.append(name)
        elif obsid != precisist and precisist not in obsids:
            MINbad.append(obsid)
            MINunique_bad.append(name)

GAMMAbad=[]
GAMMAprecisist_fx_stars=[]
GAMMAunique_bad=[]
GAMMAunique_precisist_fx_stars=[]
for id, row in unabsorbed.iterrows():
    #only care about Not always unabsorbed guys
    obsids = set(unabsorbed['# ObsID'])

    if row['always unabs']==False:
        precisist=row['precisist obsid gamma']
        obsid=row['# ObsID']
        name=row['CXO name']
        if obsid == precisist:
            GAMMAprecisist_fx_stars.append(obsid)
            GAMMAunique_precisist_fx_stars.append(name)
        elif obsid != precisist and precisist not in obsids:
            GAMMAbad.append(obsid)
            GAMMAunique_bad.append(name)

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
print('fx error version')
print(len(set(unique_bad)), 'unique objects imposters (not precisist, precisist fx isnt min abs)')
print(len(set(unique_precisist_fx_stars)), 'unique objects whose precisist fx obsid is min abs')
print()
print()
print('fx error MIN version')
print(len(set(MINunique_bad)), 'unique objects imposters (not precisist, precisist fx isnt min abs)')
print(len(set(MINunique_precisist_fx_stars)), 'unique objects whose precisist fx obsid is min abs')
print()
print()
print('gamma error version')
print(len(set(GAMMAunique_bad)), 'unique objects imposters (not precisist, precisist gamma isnt min abs)')
print(len(set(GAMMAunique_precisist_fx_stars)), 'unique objects whose precisist gamma obsid is min abs')
print()
print()

print('---------- REJECTS ----------')
print(f'luminsoity error has {len(set(unique_sloppy)-set(unique_imposters))} obj who arent in exp time version')
print(f'exp time version has {len(set(unique_imposters)-set(unique_sloppy))} obj who arent in lum error version')
print(f'{len(set(unique_sloppy)&set(unique_imposters))} are in both lum error and exp time')
print()
print(f'the two fx versions differ by {len(set(MINunique_bad)-set(unique_bad))} objs')
print()
print(f'gamma error has {len(set(GAMMAunique_bad)-set(unique_bad))} obj that arent in fx error')
print(f'fx error has {len(set(unique_bad)-set(GAMMAunique_bad))} obj that arent in gamma error')
print(f'{len(set(unique_bad)&set(GAMMAunique_bad))} are in both fx error and gamma error')

print()
print(f'fx error has {len(set(unique_bad)-set(unique_imposters))} obj who arent in exp time version')
print(f'exp time version has {len(set(unique_imposters)-set(unique_bad))} obj who arent in fx error version')
print(f'{len(set(unique_bad)&set(unique_imposters))} are in both fx error and exp time')
print()
print('is fx error same as luminosity error')

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

#bar plot for my presentation
plt.figure(figsize=(10,8))
plt.style.use('dark_background')
labels=['Errored AGN', 'Obscured AGN', 'Compton Thick AGN', 'Unobscured AGN', 'Unobscured \n Seyfert 2 AGN']
sizes=[len(input_file['CSC21P_name'].unique())-len(final_full['CXO name'].unique()),len(absorbed['CXO name'].unique()), len(compton['ids'].unique()), len(unabsorbed['CXO name'].unique()), 11]
colors=['dimgray','royalblue','orangered', 'green', 'gold']
print(np.sum(sizes))
ls=[]
for i in range(len(labels)):
    percentage = sizes[i]/np.sum(sizes)*100
    label = f'{labels[i]} \n {percentage:.1f}%'
    ls.append(label)

plt.figure(figsize=(10,10))

plt.pie(sizes, labels=ls, colors=colors)
plt.show()

#bar plot of fits or something?


### HOW TO CHOOSE WHICH OBSID TO BELIEVE
plt.figure(figsize=(10,8))
labels=['Total "min" abs', 'Always absorbed', 'Keepers','Imposters']
values=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(unique_brightest_stars)), len(set(unique_imposters))]
values2=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(unique_precisist_stars)), len(set(unique_sloppy))]
values3=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(unique_precisist_fx_stars)), len(set(unique_bad))]
values4=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(MINunique_precisist_fx_stars)), len(set(MINunique_bad))]
values5=[len(unabsorbed['CXO name'].unique()), len(always_unabsorbed), len(set(GAMMAunique_precisist_fx_stars)), len(set(GAMMAunique_bad))]

colors=['r','g','b','purple']
width=0.2
x_base = np.arange(len(labels))

# Plot the first group of bars
bar1=plt.bar(x_base - 1.5 * width, values, color=colors, width=width, label='Longest Exposure Time')

# Plot the second group of bars
bar2=plt.bar(x_base - 0.5*width, values2, color=colors, alpha=0.8, width=width, label='Smallest Luminosity Error')

bar3=plt.bar(x_base +0.5*width, values3, color=colors, alpha=0.6, width=width, label='Smallest Fx Error')

#bar4=plt.bar(x_base +  width, values4, color=colors, alpha=0.5, width=width, label='Smallest Fx Error (MIN)')

bar5=plt.bar(x_base + 1.5 * width, values5, color=colors, alpha=0.3, width=width, label='Smallest gamma error')

# Add counts above the two bar graphs
for rect in bar1 + bar2 + bar3 + bar5: 
    height = rect.get_height()
    plt.text(rect.get_x() + rect.get_width() / 2.0, height, f'{height:.0f}', ha='center', va='bottom')


# Add labels, legend, and grid
plt.xticks(x_base, labels)
plt.ylabel("Unique Objects")
plt.legend()
plt.savefig(f"/Users/kciurleo/Documents/kciurleo/AGN/plots/bargraph_minabs.pdf", format="pdf")
plt.show()

#venn diagram
sets = {
    'Exp time': set(unique_brightest_stars),
    'Luminosity': set(unique_precisist_stars),
    'FX error': set(unique_precisist_fx_stars),
    'Gamma error': set(GAMMAunique_precisist_fx_stars),
}

# Prepare data for upset plot
data = from_contents(sets)

# Create the plot
usp.UpSet(data).plot()
plt.title('number of keepers')
#plt.savefig(f"/Users/kciurleo/Documents/kciurleo/AGN/plots/upset_minabs.pdf", format="pdf")
plt.show()