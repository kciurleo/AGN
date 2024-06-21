#This file creates a target map for the sample identified in sample_identification.py
#Uncomment savefig lines to save plots as pdfs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import votable

#Read in data
seyferts=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv')
data=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv')
XMM_result = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()

#Any data filtering
portsmouth=seyferts.loc[seyferts['bpt']=='Seyfert']
agostino=seyferts.loc[seyferts['sl_class1']==1]

#Specify subsections of ra and dec desired
ras=[data['ra'], XMM_result['ra'], seyferts['ra_x'], portsmouth['ra_x']]
decs=[data['dec'],  XMM_result['dec'], seyferts['dec_x'],portsmouth['dec_x']]
colors=['silver', 'green', 'blue', 'red']
labels=['CSC2.1', 'XMM sources','Agostino Seyfert AGN Candidates','Portsmouth Seyfert AGN Candidates']
alphas=[0.5,1, 1, 1]
markers=['o','o','x','x']
sizes=[4,10,20,20]

#Make plot
fig = plt.figure(figsize=(16,10))
ax = fig.add_subplot(111, projection="aitoff")
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