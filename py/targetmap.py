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
colors=['silver', 'yellow', 'green', 'blue', 'red']
labels=['CSC2.1', 'eROSITA (Main) Sources', 'XMM Sources','Agostino Seyfert AGN Candidates','Portsmouth Seyfert AGN Candidates']
alphas=[0.5,1,1, 1, 1]
markers=['o','o','o','x','x']
sizes=[4,20,20,20,20]

#Great circle for eROSITA
#Coordinates in l, b
NGP=[0,90]
saga=[359.94423568,-0.04616002]
def galactic_to_icrs(l, b):
    galactic_coords = SkyCoord(l=l*u.degree, b=b*u.degree, frame='galactic')
    icrs_coords = galactic_coords.icrs
    return icrs_coords.ra.degree, icrs_coords.dec.degree
def great_circle_points(lon1, lat1, lon2, lat2, num_points=100):
    """ Compute points along the great circle path between two points """
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    
    # Calculate angular distance between points
    delta_lon = lon2 - lon1
    angular_distance = np.arccos(np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(delta_lon))
    
    # Create array of intermediate longitudes and latitudes
    longitudes = np.linspace(lon1, lon2, num_points)
    latitudes = np.arcsin(np.sin(lat1) * np.cos(longitudes - lon1) + np.cos(lat1) * np.sin(longitudes - lon1) * np.cos(angular_distance))
    
    return np.degrees(longitudes), np.degrees(latitudes)

# Define the points for the great circle
lon1, lat1 = 0, 90
lon2, lat2 = 60, -4
# Convert Galactic coordinates to RA and Dec
ra1, dec1 = galactic_to_icrs(lon1, lat1)
ra2, dec2 = galactic_to_icrs(lon2, lat2)

# Compute points along the great circle
longitudes, latitudes = great_circle_points(ra1, dec1, ra2, dec2)
longitudes2, latitudes2 = great_circle_points(ra2, dec2, ra1, dec1)

#Make plot
fig = plt.figure(figsize=(16,10))
ax = fig.add_subplot(111, projection="aitoff")
ax.plot(np.radians(-(((longitudes) % 360) - 180)), np.radians(latitudes), color='red', linewidth=2, label='Great Circle')
ax.plot(np.radians(-(((longitudes2) % 360) - 180)), np.radians(latitudes2), color='red', linewidth=2)
for i in range(len(ras)):
    ax.scatter(np.radians(-(((ras[i]) % 360) - 180)), np.radians(decs[i]),marker=markers[i],c=colors[i], s=sizes[i], label=labels[i], alpha=alphas[i], linewidths=0.5)
plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
                             30, 60, 90, 120, 150]),
           labels=['150°', '120°', '90°', '60°', '30°', '0°', \
                   '330°', '300°', '270°', '240°', '210°'])
plt.grid()
plt.legend(loc="upper right")
plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/target_map.pdf", format="pdf")
plt.show()