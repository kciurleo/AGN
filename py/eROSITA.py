#This file begins the process of comparing eROSITA upper limits to 
#Chandra fluxes, starting with rough calculations.

import numpy as np
import pandas as pd
from astropy.io import votable
import matplotlib.pyplot as plt

#CSC2.1 Crossmatch subset of Seyferts
seyferts = pd.read_csv("/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv")

#Result of the query in get_upper_limits.py, to retrieve upper limits for candidates in eROSITA's footprint
erosita = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/upper_limits.vot').to_table().to_pandas()

#Result of cone search of specific eROSITA target matches
cone_search=pd.read_csv("/Users/kciurleo/Documents/kciurleo/AGN/csvs/topcat_erosita.csv")

#Combine Seyferts and their upper limits
full_data=pd.merge(seyferts, erosita, on=['PLATE','FIBERID','MJD'], how='left')


#Plotting sum of eROSITA flux vs CSC flux to look for variable/changing look AGN
#Below the line is below the threshold (line is y=x)
fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 6))

#flux_aper_s, underestimate, chandra band fully contained by erosita band
ax1.scatter(full_data['UL_B_02e'], full_data['flux_aper_s'])
#y=x line
ax1.plot(np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])),
         np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])), color='red')
ax1.set_xscale('log')
ax1.set_yscale('log')
ax1.set_xlabel('0.2-5.0 keV (summed three-band) eROSITA')
ax1.set_ylabel('0.5-1.2 keV ACIS flux, bkg-subtracted, aperture-corrected')
ax1.set_title('Flux_aper_s')

#flux_aper_m, underestimate, chandra band fully contained by erosita band
ax2.scatter(full_data['UL_B_02e'], full_data['flux_aper_m'])
#y=x line
ax2.plot(np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])),
         np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])), color='red')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('0.2-5.0 keV (summed three-band) eROSITA')
ax2.set_ylabel('1.2-2 keV ACIS flux, bkg-subtracted, aperture-corrected')
ax2.set_title('Flux_aper_m')

#flux_aper_h, mismatched estimate; almost same range, different energy bands
ax3.scatter(full_data['UL_B_02e'], full_data['flux_aper_h'])
#y=x line
ax3.plot(np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])),
         np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])), color='red')
ax3.set_xscale('log')
ax3.set_yscale('log')
ax3.set_xlabel('0.2-5.0 keV (summed three-band) eROSITA')
ax3.set_ylabel('2-7 keV ACIS flux, bkg-subtracted, aperture-corrected')
ax3.set_title('Flux_aper_h')

#flux_aper_b, overestimate, erosita band almost fully contained by chandra band
ax4.scatter(full_data['UL_B_02e'], full_data['flux_aper_b'])
#y=x line
ax4.plot(np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])),
         np.linspace(np.min(full_data['UL_B_02e']), np.max(full_data['UL_B_02e'])), color='red')
ax4.set_xscale('log')
ax4.set_yscale('log')
ax4.set_xlabel('0.2-5.0 keV (summed three-band) eROSITA')
ax4.set_ylabel('0.5-7keV ACIS flux, bkg-subtracted, aperture-corrected')
ax4.set_title('Flux_aper_b')

plt.tight_layout()
plt.show(block = False)


#Compton thick search, overestimate because this is 2-7 and F_X is defined as 2-10keV
compton_upper=len(full_data.loc[full_data['flux_aper_h']/full_data['Flux_OIII_5006']<1]['CSC21P_name'].unique())

#Compton thick search, underestimate because this is .1-10 and F_X is defined as 2-10keV
compton_lower=len(full_data.loc[full_data['flux_aper_w']/full_data['Flux_OIII_5006']<1]['CSC21P_name'].unique())

print(f'There are between {compton_lower} and {compton_upper} Compton thick AGN in the Seyfert subsample')


#Histogram of separation between eROSITA and Chandra targets
plt.figure(figsize=(8,6))
plt.hist(cone_search['Separation'])
plt.xlabel('Angular separation (arcsec)')
plt.ylabel('Number of eROSITA matches')
plt.show(block=False)

#Separate run of just potential variables (i.e. the overestimates)
potential_variables = full_data.loc[full_data['flux_aper_b']>full_data['UL_B_02e']]['CSC21P_name']

obsids = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv')

interest = pd.merge(potential_variables, obsids, on='CSC21P_name')

interest = interest.drop_duplicates(subset=['CSC21P_name', 'ra_x', 'dec_x','CHANDRA_OBSID'])
#interest.to_csv('/Users/kciurleo/Documents/kciurleo/temporary_variable_run/coords.csv', index=False)

#Which (temporary) guys have fluxes greater than their eROSITA upper limits?
temporary_variable_run = pd.read_csv('/Users/kciurleo/Documents/kciurleo/temporary_variable_run/final_data/final_info_full.csv')

new_interest = pd.merge(temporary_variable_run, full_data, left_on=['CXO name'], right_on=['CSC21P_name'], how='left')

new_interest[['Soft flux', 'Medium flux', 'Hard flux', 'Sum flux']] = new_interest[['Soft flux', 'Medium flux', 'Hard flux', 'Sum flux']].apply(pd.to_numeric, errors='coerce', downcast='float')

#Soft 
soft = new_interest.loc[new_interest['Soft flux']>new_interest['UL_B_021']]

#Medium
medium = new_interest.loc[new_interest['Medium flux']>new_interest['UL_B_022']]

#Hard
hard = new_interest.loc[new_interest['Hard flux']>new_interest['UL_B_023']]

#Summed
summed = new_interest.loc[new_interest['Sum flux']>new_interest['UL_B_02e']]

print(f'There are {len(soft["CSC21P_name"].unique())} unique objects whose soft flux exceeds their eROSITA upper limit.')
print(f'There are {len(medium["CSC21P_name"].unique())} unique objects whose medium flux exceeds their eROSITA upper limit.')
print(f'There are {len(hard["CSC21P_name"].unique())} unique objects whose hard flux exceeds their eROSITA upper limit.')
print(f'There are {len(summed["CSC21P_name"].unique())} unique objects whose summed flux exceeds their eROSITA upper limit.')

#The trial run only had medium ones which this was true for, so:
med_yes = []
for id, row in summed.iterrows():
    if row['CSC21P_name'] in medium["CSC21P_name"].unique():
        med_yes.append(True)
    else:
        med_yes.append(False)

summed['med_excess_yes'] = med_yes

unique_summed = summed.drop_duplicates(subset=['# ObsID', 'IAUstripped'])

#unique_summed.to_csv('/Users/kciurleo/Documents/kciurleo/temporary_variable_run/final_data/unique_summed.csv', index=False)

print(unique_summed[['IAUstripped', '# ObsID', 'model', 'counts', 'Sum flux', 'med_excess_yes']])