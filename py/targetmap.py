#This file creates a target map for the sample identified in sample_identification.py
#Uncomment savefig lines to save plots as pdfs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import votable
from astropy.coordinates import SkyCoord
import astropy.units as u

#Read in data
seyferts=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv')
data=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv')
XMM_result = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()
erosita = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/topcat_erosita.csv')
final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')
s2s_xmm = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/xmm_proposal_s2s.csv')

#identify point sources w/SDSS data
sources = data.dropna(subset=['Sep_SPEC_CSC21P'])
point_sources = sources.loc[sources['extent_flag']==False]

#identify unabsorbed
unabsorbed=final_full.loc[final_full['unabsorbed']==True]

#Any data filtering
portsmouth=seyferts.loc[seyferts['bpt']=='Seyfert']
agostino=seyferts.loc[seyferts['sl_class1']==1]

#Specify subsections of ra and dec desired
'''
ras=[data['ra'], erosita['ra_cone'], XMM_result['ra'], seyferts['ra_x'], portsmouth['ra_x']]
decs=[data['dec'],  erosita['dec_cone'], XMM_result['dec'], seyferts['dec_x'],portsmouth['dec_x']]
colors=['dimgrey', 'yellow', 'deepskyblue', 'lime', 'red']
labels=['CSC2.1', 'eROSITA (Main) Sources', 'XMM Sources','Agostino Seyfert AGN Candidates','Portsmouth Seyfert AGN Candidates']
alphas=[0.15,1,1, 1, 1]
markers=['o','o','o','x','x']
sizes=[4,20,20,20,20]
'''
'''
#fiddly ones
ras=[data['ra'], point_sources['ra'], pd.concat([agostino['ra_x'],portsmouth['ra_x']]), unabsorbed['RA'], s2s_xmm['RA']]
decs=[data['dec'], point_sources['dec'], pd.concat([agostino['dec_x'],portsmouth['dec_x']]), unabsorbed['Dec'], s2s_xmm['Dec']]
colors=['dimgrey', 'royalblue', 'red', 'lime', 'gold']
labels=['Chandra Source Catalog', 'SDSS Counterparts', 'AGN', 'Unabsorbed AGN', 'Preliminary Seyfert 2s']
alphas=[.15, .15, .25, .25, 1]
markers=['o', 'o', 'x', 'x', '*']
sizes=[4,4,20, 20, 60]
'''

print(len(data['CSC21P_name'].unique()))
print(len(point_sources['CSC21P_name'].unique()))
print(len(set(agostino['CSC21P_name'])|set(portsmouth['CSC21P_name'])))
print(len(unabsorbed['CXO name'].unique()))
print(len(s2s_xmm['CXO name'].unique()))

ras=[data['ra'], point_sources['ra'], pd.concat([agostino['ra_x'],portsmouth['ra_x']])]
decs=[data['dec'], point_sources['dec'], pd.concat([agostino['dec_x'],portsmouth['dec_x']])]
colors=['dimgrey', 'royalblue', 'red']
labels=['Chandra Source Catalog', 'SDSS Counterparts', 'AGN']
alphas=[.15, .15,  1]
markers=['o', 'o',  'x']
sizes=[4,4,60]

#Meridian at SagA*, where eROSITA cuts off
lon_meridian = 359.94423568 * u.deg
lat_array = np.linspace(-90, 90, 2000) * u.deg  # Latitude array from -90 to 90 degrees

#Circle array in galactic coords
galactic_coords = SkyCoord(l=lon_meridian, b=lat_array, frame='galactic')
#Converted to equatorial coords
equatorial_coords = galactic_coords.transform_to('fk5')

#RA/dec of circle
RA = equatorial_coords.ra.degree
Dec = equatorial_coords.dec.degree

#Flip RA axis
def flip(ra):
    #flips map's RA coordinate
    return(-ra)

#Make plot
fig = plt.figure(figsize=(16,10))
plt.style.use('dark_background')
ax = fig.add_subplot(111, projection="aitoff")
'''
#eROSITA
ax.plot(flip(np.radians(RA-180)), np.radians(Dec), '.',markersize=1, color='yellow')
ax.plot(flip(np.radians(RA-360)), -np.radians(Dec), '.',markersize=1, color='yellow', label='eROSITA Boundary')
#weird connecting line
ax.plot(flip(np.array([np.radians(RA[-1]-180), np.radians(RA[150]-360)])),[np.radians(Dec[-1]), -np.radians(Dec[150])],color='yellow', linestyle='-')
'''

for i in range(len(ras)):
    ax.scatter(flip(np.radians(ras[i]-180)), np.radians(decs[i]),marker=markers[i],c=colors[i], s=sizes[i], label=labels[i], alpha=alphas[i], linewidths=1)
#plot twice for all the shifting
for i in range(len(ras)):
    ax.scatter(flip(np.radians(ras[i]-360-180)), np.radians(decs[i]),marker=markers[i],c=colors[i], s=sizes[i], alpha=alphas[i], linewidths=0.5)

plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150]),
           #for unflipped
           #labels=['30°', '60°', '90°', '120°', '150°', '180°', '210°', '240°', '270°', '300°', '330°'])
           labels=['330°', '300°', '270°', '240°',  '210°', '180°', '150°', '120°', '90°','60°', '30°'])

plt.grid()
plt.legend(loc="upper right")
plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/map3.png", dpi=250)
#plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/target_map.pdf", format="pdf")
plt.show()