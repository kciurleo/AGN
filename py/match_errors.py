import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from ciao_contrib.region.check_fov import FOVFiles
from ciao_contrib.runtool import *
import glob
import re
import matplotlib.colors as mcolors

seyferts = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_process_input.csv')[['CSC21P_name', 'CHANDRA_OBSID', ' OBSDATE', ' TIME', 'MJD','PLATE','FIBERID']]
match_errors = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_error_srcflux.csv')
final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',engine='python',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
#csc21=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv', low_memory=False)
combined_match_errors = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_errors_with_fluxes.csv')
'''
nums=[]
presents=[]
for i, row in match_errors.iterrows():
    #Get the total number of obsids for a given name
    subdude=seyferts.loc[seyferts['CSC21P_name']==row['NAME']]
    num = len(subdude['CHANDRA_OBSID'].unique())
    nums.append(num)

    #Get whether or not the thing is in the fov file
    try:
        file = glob.glob(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/*fov1.fits*')[0]
    except:
        presents.append(np.nan)

    my_obs=FOVFiles(file)
    ii=my_obs.inside(row["RA"], row["DEC"])
    if len(ii)==0:
        presents.append(False)
    else:
        presents.append(True)
    print(f'finished {row["NAME"]}')


match_errors['NUM']=nums
match_errors['PRESENT']=presents

#match_errors.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_error_srcflux.csv', index=False)

#print(match_errors)

'''

#Those who are present or not in their FOV
present = match_errors.loc[match_errors['PRESENT']==True]
not_present = match_errors.loc[match_errors['PRESENT']==False]

#Unique targets 
present_unique=present.drop_duplicates(subset=['NAME'])
not_present_unique=not_present.drop_duplicates(subset=['NAME'])

#Whether those targets which are present have another obsid which they might have matched
present_only_one=present_unique.loc[present_unique['NUM']==1]
present_multiple=present_unique.loc[present_unique['NUM']>1]
not_present_only_one=not_present_unique.loc[not_present_unique['NUM']==1]
not_present_multiple=not_present_unique.loc[not_present_unique['NUM']>1]

#Check to make sure all the guys who have multiple have at least one obs where they were matched
yes_list=[]

for i, row in present_multiple.iterrows():
    subdude=final_list.loc[final_list['NAME']==row['NAME']]
    for i2, row2 in subdude.iterrows():
        #As long as one of the obsids has counts instead of 'no match' we're good
        if row2['COUNTS']!='NO MATCH':
            yes_list.append(row['NAME'])
            break

second_yes_list=[]

for i, row in not_present_multiple.iterrows():
    subdude=final_list.loc[final_list['NAME']==row['NAME']]
    for i2, row2 in subdude.iterrows():
        #As long as one of the obsids has counts instead of 'no match' we're good
        if row2['COUNTS']!='NO MATCH':
            second_yes_list.append(row['NAME'])
            break

#Those whose multiples have at least one obs where they were matched
safe_present_multiple = present_multiple[present_multiple['NAME'].isin(yes_list)]
safe_not_present_multiple = not_present_multiple[not_present_multiple['NAME'].isin(second_yes_list)]

#Those who don't
bad_present_multiple = present_multiple[~present_multiple['NAME'].isin(yes_list)]
bad_not_present_multiple = not_present_multiple[~not_present_multiple['NAME'].isin(second_yes_list)]

#Those who are present in their FOV who have no matched obsids at all
all_naughty_guys = bad_present_multiple.merge(present_only_one, how='outer')

print(f"{len(present['NAME'])} of {len(match_errors['NAME'])} obsid-object combos are present on the chips.")
print(f"{len(not_present['NAME'])} of {len(match_errors['NAME'])} obsid-object combos are on chip gaps (outside the FOV file)")
print()
print(f'Of those obsid-object combos present in their observations, there are {len(present_unique["NAME"])} unique objects.')
print(f'Out of these unique objects, {len(present_only_one["NAME"])} are the only observation of their object and {len(present_multiple["NAME"])} objects have other observations.')
print()
print(f'Of those with multiple observations, {len(safe_present_multiple["NAME"])} have at least one observation which was matched.')
print(f'{len(bad_present_multiple["NAME"])} had match errors for all their multiple observations.')
print()
print(f'Of those obsid-object combos not present in their observations, there are {len(not_present_unique["NAME"])} unique objects.')
print(f'Out of these unique objects, {len(not_present_only_one["NAME"])} are the only observation of their object and {len(not_present_multiple["NAME"])} objects have other observations.')
print()
print(f'Of those with multiple observations, {len(safe_not_present_multiple["NAME"])} have at least one observation which was matched.')
print(f'{len(bad_not_present_multiple["NAME"])} had match errors for all their multiple observations.')
print()
print(f'There are therefore {len(all_naughty_guys["NAME"])} objects which are present on their chips but are unmatched in all their observations (either one or multiple).')

plt.figure(figsize=(8,6))
plt.hist(all_naughty_guys['counts'], bins=40)
plt.title('Matching Errors - Present Fully Unmatched Objects')
plt.xlabel('Counts')
plt.show()

#check the date for all the bright ones
print(all_naughty_guys.loc[all_naughty_guys['counts']>25][['NAME','OBSID','date']])
print(bad_not_present_multiple[['NAME','OBSID','date']])
'''
#Get the band counts for chandra from csc2.1 file
combined_match_errors=pd.merge(match_errors, csc21, how="left", left_on='NAME', right_on="CSC21P_name")
hms =[]
hss=[]
mss=[]

#Get hardness ratios from the csc catalog
for id, row in combined_match_errors.iterrows():
    print('querying for ',row['NAME'])
    try:
        result = search_csc(row['NAME'], radius=0.02, columns=['o.hard_hm', 'o.hard_hs', 'o.hard_ms'])
        result=result.split('\n')[21:23]
        split_rows = [re.split(r'\s+', row.strip()) for row in result]

        #add them in
        hms.append(split_rows[1][-3])
        hss.append(split_rows[1][-2])
        mss.append(split_rows[1][-1])
    except:
        #if there's any problem (meaning the name wasn't resolved or the result returned 0 rows, do nans)
        #doing this because we care about statistical sample, not tracking down every single tiny little error
        hms.append(np.nan)
        hss.append(np.nan)
        mss.append(np.nan)
        continue

combined_match_errors['hm']=hms
combined_match_errors['hs']=hss
combined_match_errors['ms']=mss
combined_match_errors.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_errors_with_fluxes.csv')
print(combined_match_errors[['NAME','OBSID','RA','DEC','counts','NUM','PRESENT','flux_aper_b','flux_aper_h','flux_aper_m','flux_aper_s','flux_aper_w','hm','hs','ms']])
'''

#Making histograms for the flux in different bands
fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(8,10))

ax1, ax2, ax3, ax4, ax5 = axes.flatten()
cstat_bins=50

ax1.hist(combined_match_errors['flux_aper_b'], bins = cstat_bins)
ax1.set_xlabel('flux_aper_b')

ax2.hist(combined_match_errors['flux_aper_h'], bins = cstat_bins)
ax2.set_xlabel('flux_aper_h')

ax3.hist(combined_match_errors['flux_aper_m'], bins = cstat_bins)
ax3.set_xlabel('flux_aper_m')

ax4.hist(combined_match_errors['flux_aper_s'], bins = cstat_bins)
ax4.set_xlabel('flux_aper_s')

ax5.hist(combined_match_errors['flux_aper_w'], bins = cstat_bins)
ax5.set_xlabel('flux_aper_w')

plt.tight_layout()
plt.show(block=False)

#color color diagram (but make it fancy)
present_multiple = combined_match_errors[(combined_match_errors['PRESENT']) & (combined_match_errors['NUM'] > 1)]
present_single = combined_match_errors[(combined_match_errors['PRESENT']) & (combined_match_errors['NUM'] == 1)]
present_false = combined_match_errors[~combined_match_errors['PRESENT']]

cmap = plt.get_cmap('rainbow')
norm = mcolors.PowerNorm(gamma=0.5, vmin=combined_match_errors['counts'].min(), vmax=combined_match_errors['counts'].max())

fig, ax = plt.subplots(figsize=(10, 10))

sc1 = ax.scatter(present_multiple['hm'], present_multiple['ms'], s=24, marker='o', c=present_multiple['counts'], cmap=cmap, norm=norm, label='Present in Multiple Obsid')
sc2 = ax.scatter(present_single['hm'], present_single['ms'], s=24, marker='s', c=present_single['counts'], cmap=cmap, norm=norm, label='Present in Single Obsid')
sc3 = ax.scatter(present_false['hm'], present_false['ms'], s=24, marker='x', c=present_false['counts'], cmap=cmap, norm=norm, label='On Chip Gap')

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, label='Counts')

ax.set_xlabel('(h-m)/(h+m)')
ax.set_ylabel('(m-s)/(m+s)')
ax.legend(loc='upper left')
ax.set_title('Color-color Diagram of Match Errors')
plt.savefig('/Users/kciurleo/Documents/kciurleo/AGN/plots/mattch_error_cc.pdf', format='pdf')
plt.show()