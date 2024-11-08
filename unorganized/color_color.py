import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
from ciao_contrib.runtool import *
import glob
import re
import matplotlib.colors as mcolors
from matplotlib.colors import LogNorm, PowerNorm

#Get the band counts for chandra from csc2.1 file
final_min_abs = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_min_abs_full.csv')
final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')
#csc21=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv', low_memory=False)
linewidths=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/line_widths_seyferts.csv')
point_sources=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/point_sources.csv')
'''
combined_full=pd.merge(final_list, csc21, how="left", left_on='NAME', right_on="CSC21P_name")
hms =[]
hss=[]
mss=[]

#Get hardness ratios from the csc catalog
for id, row in combined_full.iterrows():
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

combined_full['hm']=hms
combined_full['hs']=hss
combined_full['ms']=mss
combined_full.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/all_guys_with_fluxes.csv')
#print(combined_full[['NAME','OBSID','RA','DEC','counts','NUM','PRESENT','flux_aper_b','flux_aper_h','flux_aper_m','flux_aper_s','flux_aper_w','hm','hs','ms']])
'''
combined_full=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/all_guys_with_fluxes.csv')
'''
#color color diagram (but make it fancy)
present_multiple = combined_full[(combined_full['PRESENT']) & (combined_full['NUM'] > 1)]
present_single = combined_full[(combined_full['PRESENT']) & (combined_full['NUM'] == 1)]
present_false = combined_full[~combined_full['PRESENT']]

cmap = plt.get_cmap('rainbow')
norm = mcolors.PowerNorm(gamma=0.5, vmin=combined_full['counts'].min(), vmax=combined_full['counts'].max())

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

plt.show()
'''
#get some linewidths in there
linewidths=linewidths.merge(point_sources, how="left", left_on=['plate', 'mjd', 'fiberID'], right_on=['PLATE', 'MJD','FIBERID'])
final_full=pd.merge(linewidths, final_full, how="right", left_on='CSC21P_name', right_on="CXO name")


extra_combined=pd.merge(combined_full, final_full, how="left", left_on='NAME', right_on="CXO name")

#define some subgroups
unmatched = combined_full.loc[combined_full['COUNTS'] == 'NO MATCH']
compton_thick = extra_combined.loc[extra_combined['compton thick'] == 'True']
unabsorbed = extra_combined.loc[extra_combined['unabsorbed'] == True]

# Print unabsorbed column
print(unabsorbed['unabsorbed'])

fig, ax = plt.subplots(figsize=(10, 10))

# Scatter plot for everybody
sc1 = ax.scatter(combined_full['hm'], combined_full['ms'], s=24,alpha=0.5, c='orange',marker='o', label='everybody')
# Scatter plot for unmatched
sc2 = ax.scatter(unmatched['hm'], unmatched['ms'], s=20, marker='d', c='blue',alpha=0.5,label='unmatched')

# Scatter plot for compton thick based on model
compton_main = compton_thick[compton_thick['model'] == 'main']
compton_res = compton_thick[compton_thick['model'] == 'res']
sc3_main = ax.scatter(compton_main['hm'], compton_main['ms'], c='green',s=24, marker='o', label='compton thick (main)')
sc3_res = ax.scatter(compton_res['hm'], compton_res['ms'], c='green',s=24, marker='s', label='compton thick (res)')

# Scatter plot for unabsorbed based on model
unabsorbed_main = unabsorbed[unabsorbed['model'] == 'main']
unabsorbed_res = unabsorbed[unabsorbed['model'] == 'res']
sc4_main = ax.scatter(unabsorbed_main['hm'], unabsorbed_main['ms'],c='red', s=28, marker='+', label='unabsorbed (main)')
sc4_res = ax.scatter(unabsorbed_res['hm'], unabsorbed_res['ms'],c='red', s=28, marker='x', label='unabsorbed (res)')

# Set labels and legend
ax.set_xlabel('(h-m)/(h+m)')
ax.set_ylabel('(m-s)/(m+s)')
ax.legend(loc='upper left')
ax.set_title('Color-color (model-independent photon flux)')

#plt.savefig('/Users/kciurleo/Documents/kciurleo/AGN/plots/color_color.pdf', format='pdf')
plt.show(block=False)

#Now do the same with the calculated fluxes
final_full['Hard flux'] = pd.to_numeric(final_full['Hard flux'], errors='coerce')
final_full['Medium flux'] = pd.to_numeric(final_full['Medium flux'], errors='coerce')
final_full['Soft flux'] = pd.to_numeric(final_full['Soft flux'], errors='coerce')
final_full['hm']=(final_full['Hard flux']-final_full['Medium flux'])/(final_full['Hard flux']+final_full['Medium flux'])
final_full['ms']=(final_full['Medium flux']-final_full['Soft flux'])/(final_full['Soft flux']+final_full['Medium flux'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Scatter plot for everybody
sc1 = ax1.scatter(final_full['hm'], final_full['ms'],c=final_full['Sigma_Hb_4861'], cmap='pink', s=28,alpha=0.75, marker='o', label='everybody', norm=PowerNorm(gamma=.4))
cbar = plt.colorbar(sc1, ax=ax1)
cbar.set_label('Sigma_Hb_4861')
# Scatter plot for unmatched
#sc2 = ax.scatter(unmatched['hm'], unmatched['ms'], s=20, marker='d', c='blue',alpha=0.5,label='unmatched')
#nonexistent in final full bc they didn't go through the pipeline

#second graph
sc12 = ax2.scatter(final_full['hm'], final_full['ms'],c=final_full['Sigma_Ha_6562'], cmap='pink', s=28,alpha=0.75, marker='o', label='everybody', norm=PowerNorm(gamma=.4))
cbar2 = plt.colorbar(sc12, ax=ax2)
cbar2.set_label('Sigma_Ha_6562')

compton_thick = final_full.loc[final_full['compton thick'] == 'True']
unabsorbed = final_full.loc[(final_full['unabsorbed'] == True) & (final_full['compton thick'] == 'False')]
test_guys=final_full.loc[(final_full['unabsorbed'] == False) & (final_full['compton thick'] == 'False')]

# Scatter plot for compton thick based on model
compton_main = compton_thick[compton_thick['model'] == 'main']
compton_res = compton_thick[compton_thick['model'] == 'res']
sc3_main = ax1.scatter(compton_main['hm'], compton_main['ms'], c='green',s=24, marker='+', label='compton thick (main)')
sc3_res = ax1.scatter(compton_res['hm'], compton_res['ms'], c='green',s=24, marker='x', label='compton thick (res)')

sc3_main2 = ax2.scatter(compton_main['hm'], compton_main['ms'], c='green',s=24, marker='+', label='compton thick (main)')
sc3_res2 = ax2.scatter(compton_res['hm'], compton_res['ms'], c='green',s=24, marker='x', label='compton thick (res)')


# Scatter plot for unabsorbed based on model
unabsorbed_main = unabsorbed[unabsorbed['model'] == 'main']
unabsorbed_res = unabsorbed[unabsorbed['model'] == 'res']
sc4_main = ax1.scatter(unabsorbed_main['hm'], unabsorbed_main['ms'],c='red', s=28, marker='+', label='unabsorbed (main)')
sc4_res = ax1.scatter(unabsorbed_res['hm'], unabsorbed_res['ms'],c='red', s=28, marker='x', label='unabsorbed (res)')

sc4_main2 = ax2.scatter(unabsorbed_main['hm'], unabsorbed_main['ms'],c='red', s=28, marker='+', label='unabsorbed (main)')
sc4_res2 = ax2.scatter(unabsorbed_res['hm'], unabsorbed_res['ms'],c='red', s=28, marker='x', label='unabsorbed (res)')


# Set labels and legend
ax1.set_xlabel('(h-m)/(h+m)')
ax1.set_ylabel('(m-s)/(m+s)')
ax1.legend(loc='upper left')
ax1.set_ylim(0.25,1.10)

ax2.set_xlabel('(h-m)/(h+m)')
ax2.set_ylabel('(m-s)/(m+s)')
ax2.legend(loc='upper left')
plt.suptitle('Color-color (model-dependent flux)', size=20)
ax2.set_ylim(0.25,1.10)

plt.savefig('/Users/kciurleo/Documents/kciurleo/AGN/plots/color_color_model_dep.pdf', format='pdf')
plt.show()
