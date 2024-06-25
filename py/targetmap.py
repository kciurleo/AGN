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

#Any data filtering
portsmouth=seyferts.loc[seyferts['bpt']=='Seyfert']
agostino=seyferts.loc[seyferts['sl_class1']==1]

#Specify subsections of ra and dec desired
ras=[data['ra'], erosita['ra_cone'], XMM_result['ra'], seyferts['ra_x'], portsmouth['ra_x']]
decs=[data['dec'],  erosita['dec_cone'], XMM_result['dec'], seyferts['dec_x'],portsmouth['dec_x']]
colors=['dimgrey', 'yellow', 'deepskyblue', 'lime', 'red']
labels=['CSC2.1', 'eROSITA (Main) Sources', 'XMM Sources','Agostino Seyfert AGN Candidates','Portsmouth Seyfert AGN Candidates']
alphas=[0.15,1,1, 1, 1]
markers=['o','o','o','x','x']
sizes=[4,20,20,20,20]

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

#Make plot
fig = plt.figure(figsize=(16,10))
plt.style.use('dark_background')
ax = fig.add_subplot(111, projection="aitoff")

#eROSITA
ax.plot(np.radians(RA-180), np.radians(Dec), '.',markersize=1, color='yellow')
ax.plot(np.radians(RA-360), -np.radians(Dec), '.',markersize=1, color='yellow', label='eROSITA Boundary')
#weird connecting line
ax.plot([np.radians(RA[-1]-180), np.radians(RA[150]-360)],[np.radians(Dec[-1]), -np.radians(Dec[150])],color='yellow', linestyle='-')


for i in range(len(ras)):
    ax.scatter(np.radians(ras[i]-180), np.radians(decs[i]),marker=markers[i],c=colors[i], s=sizes[i], label=labels[i], alpha=alphas[i], linewidths=1)
#plot twice because it doesn't like to do that
for i in range(len(ras)):
    ax.scatter(np.radians(ras[i]-360-180), np.radians(decs[i]),marker=markers[i],c=colors[i], s=sizes[i], alpha=alphas[i], linewidths=0.5)

plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
                             30, 60, 90, 120, 150]),
           labels=['30°', '60°', '90°', '120°', '150°', '180°', \
                   '210°', '240°', '270°', '300°', '330°'])

plt.grid()
plt.legend(loc="upper right")

plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/target_map.pdf", format="pdf")
plt.show()