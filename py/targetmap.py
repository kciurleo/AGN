#This file creates a target map for the sample identified in sample_identification.py
#Uncomment savefig lines to save plots as pdfs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Read in data
seyferts=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv')
data=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv')

#Specify subsections of ra and dec desired
ras=[data['ra'], seyferts['ra_x']]
decs=[data['dec'], seyferts['dec_x']]
colors=['silver', 'red']
labels=['CSC2.1','Seyfert AGN Candidates']
alphas=[0.5,1]

#Make plot
fig = plt.figure(figsize=(12,8))
ax = fig.add_subplot(111, projection="aitoff")
for i in range(len(ras)):
    ax.scatter(np.radians(-(((ras[i]) % 360) - 180)), np.radians(decs[i]), c=colors[i], s=4, label=labels[i], alpha=alphas[i])
plt.xticks(ticks=np.radians([-150, -120, -90, -60, -30, 0, \
                             30, 60, 90, 120, 150]),
           labels=['150°', '120°', '90°', '60°', '30°', '0°', \
                   '330°', '300°', '270°', '240°', '210°'])
plt.grid()
plt.legend(loc="upper right")
plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/target_map.pdf", format="pdf")
plt.show()