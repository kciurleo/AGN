#This file creates a BPT diagram for the sample identified in sample_identification.py
#Uncomment savefig lines to save plots as pdfs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Note to self: need to add errors correctly

#Read in data
full_point_sources=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_point_sources.csv')
final_min_abs = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_min_abs_full.csv')

#Find only Seyfert Galaxies, classified as bpt="Seyfert" for Portsmouth and sl_class1=1 for Agostino (latter is specifically Seyfert 2s)
portsmouth_s2=full_point_sources.loc[full_point_sources['bpt']=="Seyfert"]
agostino_s2=full_point_sources.loc[full_point_sources['sl_class1']==1]

#Find starforming galaxies, bpt="Star Forming" or "Star Fo", Agostino general emission line classification = 1 star forming, = 4 is "more likely star forming than S/L"
starforming=full_point_sources.loc[(full_point_sources['bpt']=="Star Forming") | (full_point_sources['bpt']=="Star Fo") | (full_point_sources['gen_el_class']==1) | (full_point_sources['gen_el_class']==4)]

#Find composite galaxies, only identified by Portsmouth
composite=full_point_sources.loc[(full_point_sources['bpt']=="Composite") | (full_point_sources['bpt']=="Composi")]

#Min abs versions
full_min_abs=final_min_abs.merge(full_point_sources, how='left', right_on='CSC21P_name', left_on='CXO name')

#Ke01 SFR cutoffs from Kewley et al. (2006)
kxNII=np.linspace(-4,0.4,1000)
ke01NII=0.61/(kxNII-0.47)+1.19

kxSII=np.linspace(-4,0.2,1000)
ke01SII=0.72/(kxSII-0.32)+1.30

kxOI=np.linspace(-4,-.8,1000)
ke01OI=0.73/(kxOI+0.59)+1.33

#Ka03 pure star formation line, for [NII] only
kaxNII=np.linspace(-1.2,-.01,1000)
ka03NII=0.61/(kaxNII-0.05)+1.3

#Seyfert/LINER distinctions, for [SII] and [OI] only
slxSII=np.linspace(-0.3,.75,1000)
slSII=1.89*slxSII+0.76

slxOI=np.linspace(-1.1,0,1000)
slOI=1.18*slxOI+1.3

'''
#basic bpt diagrams
plt.figure(figsize=(6,6))

plt.scatter(np.log10(full_point_sources['Flux_NII_6583']/full_point_sources['Flux_Ha_6562']),np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']), s=3,c='gray',marker='.', alpha=0.5, label='CSC Point Sources')
plt.scatter(np.log10(composite['Flux_NII_6583']/composite['Flux_Ha_6562']),np.log10(composite['Flux_OIII_5006']/composite['Flux_Hb_4861']), s=3,c='green',marker='.', alpha=0.5, label='Composites')
plt.scatter(np.log10(starforming['Flux_NII_6583']/starforming['Flux_Ha_6562']),np.log10(starforming['Flux_OIII_5006']/starforming['Flux_Hb_4861']), s=3,c='yellow',marker='.', alpha=0.5, label='Star-Forming')
plt.scatter(np.log10(agostino_s2['Flux_NII_6583']/agostino_s2['Flux_Ha_6562']),np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']), marker='.', s=3, c='blue', label='Agostino Seyferts')
plt.scatter(np.log10(portsmouth_s2['Flux_NII_6583']/portsmouth_s2['Flux_Ha_6562']),np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']), marker='.', s=3, c='red', label='Portsmouth Seyferts')
plt.plot(kxNII, ke01NII, color='black', linestyle='dashed',label='Ke01')
plt.plot(kaxNII, ka03NII, color='black', linestyle='dotted',label='Ka03')

plt.xlabel("log([NII]λ6583/Hα)")
plt.ylabel("log([OIII]λ5006/Hβ)")
#note these limits are here because of some weird outliers
plt.xlim(-2.5,1.5)
plt.ylim(-2,2.5)
plt.legend(loc='lower left')

#plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/sample_bpt_single.pdf", format="pdf")
plt.show(block=False)

#BPT diagrams in one plot
fig, axs = plt.subplots(1, 3, figsize=(20, 6), sharey=True, gridspec_kw={'wspace': 0.1})

#NII
axs[0].scatter(np.log10(full_point_sources['Flux_NII_6583']/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               s=4, c='gray', marker='.', alpha=0.5, label='CSC Point Sources')
axs[0].scatter(np.log10(agostino_s2['Flux_NII_6583']/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino')
axs[0].scatter(np.log10(portsmouth_s2['Flux_NII_6583']/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth')
axs[0].plot(kxNII, ke01NII, color='black', linestyle='dashed', label='Ke01')
axs[0].plot(kaxNII, ka03NII, color='black', linestyle='dotted', label='Ka03')
axs[0].set_xlabel("log([NII]λ6583/Hα)", fontsize=14)
axs[0].set_ylabel("log([OIII]λ5006/Hβ)", fontsize=14)
#note these limits are here because of some weird outliers
axs[0].set_xlim(-2.5, 1.5)
axs[0].set_ylim(-2,2.5)
axs[0].legend(loc='lower left')

#SII
axs[1].scatter(np.log10((full_point_sources['Flux_SII_6730']+full_point_sources['Flux_SII_6716'])/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               marker='.', s=4, color='gray', alpha=0.5, label='CSC Point Sources')
axs[1].scatter(np.log10((agostino_s2['Flux_SII_6730']+agostino_s2['Flux_SII_6716'])/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino')
axs[1].scatter(np.log10((portsmouth_s2['Flux_SII_6730']+portsmouth_s2['Flux_SII_6716'])/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth')
axs[1].plot(kxSII, ke01SII, color='black', linestyle='dashed', label='Maximum Starburst')
axs[1].plot(slxSII, slSII, color='black', linestyle='-.', label='Seyfert-LINER')
axs[1].set_xlabel("log(([SII]λ6716 + [SII]λ6730)/Hα)", fontsize=14)
axs[1].set_xlim(-2, 1.5)
axs[1].set_ylim(-2,2.5)
axs[1].legend(loc='lower left')

#OI
axs[2].scatter(np.log10((full_point_sources['Flux_OI_6363'])/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               marker='.', s=4, color='gray', alpha=0.5, label='CSC Point Sources')
axs[2].scatter(np.log10((agostino_s2['Flux_OI_6363'])/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino')
axs[2].scatter(np.log10((portsmouth_s2['Flux_OI_6363'])/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth')
axs[2].plot(kxOI, ke01OI, color='black', linestyle='dashed', label='Maximum Starburst')
axs[2].plot(slxOI, slOI, color='black', linestyle='-.', label='Seyfert-LINER')
axs[2].set_xlabel("log([OI]λ6363/Hα)", fontsize=14)
axs[2].set_xlim(-3, 0.75)
axs[2].set_ylim(-2,2.5)
axs[2].legend(loc='lower left')

#plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/sample_bpt.pdf", format="pdf")
plt.show()
'''

#bpt diagram for sample
#BPT diagrams in one plot
fig, axs = plt.subplots(1, 3, figsize=(20, 6), sharey=True, gridspec_kw={'wspace': 0.1})

#NII
axs[0].scatter(np.log10(full_point_sources['Flux_NII_6583']/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               s=4, c='gray', marker='.', alpha=0.25, label='CSC Point Sources')
axs[0].scatter(np.log10(agostino_s2['Flux_NII_6583']/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino', alpha=0.5)
axs[0].scatter(np.log10(portsmouth_s2['Flux_NII_6583']/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth', alpha=0.5)
axs[0].scatter(np.log10(full_min_abs['Flux_NII_6583']/full_min_abs['Flux_Ha_6562']),
               np.log10(full_min_abs['Flux_OIII_5006_x']/full_min_abs['Flux_Hb_4861']),
               s=8, c='black', marker='*', alpha=1, label='Min Abs AGN Candidates')
axs[0].plot(kxNII, ke01NII, color='black', linestyle='dashed', label='Ke01')
axs[0].plot(kaxNII, ka03NII, color='black', linestyle='dotted', label='Ka03')
axs[0].set_xlabel("log([NII]λ6583/Hα)", fontsize=14)
axs[0].set_ylabel("log([OIII]λ5006/Hβ)", fontsize=14)
#note these limits are here because of some weird outliers
axs[0].set_xlim(-2.5, 1.5)
axs[0].set_ylim(-2,2.5)
axs[0].legend(loc='lower left')

#SII
axs[1].scatter(np.log10((full_point_sources['Flux_SII_6730']+full_point_sources['Flux_SII_6716'])/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               marker='.', s=4, color='gray', alpha=0.25, label='CSC Point Sources')
axs[1].scatter(np.log10((agostino_s2['Flux_SII_6730']+agostino_s2['Flux_SII_6716'])/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino', alpha=0.5)
axs[1].scatter(np.log10((portsmouth_s2['Flux_SII_6730']+portsmouth_s2['Flux_SII_6716'])/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth', alpha=0.5)
axs[1].scatter(np.log10((full_min_abs['Flux_SII_6730']+full_min_abs['Flux_SII_6716'])/full_min_abs['Flux_Ha_6562']),
               np.log10(full_min_abs['Flux_OIII_5006_x']/full_min_abs['Flux_Hb_4861']),
               marker='*', s=8, color='black', alpha=1, label='Min Abs AGN Candidates')
axs[1].plot(kxSII, ke01SII, color='black', linestyle='dashed', label='Maximum Starburst')
axs[1].plot(slxSII, slSII, color='black', linestyle='-.', label='Seyfert-LINER')
axs[1].set_xlabel("log(([SII]λ6716 + [SII]λ6730)/Hα)", fontsize=14)
axs[1].set_xlim(-2, 1.5)
axs[1].set_ylim(-2,2.5)
axs[1].legend(loc='lower left')

#OI
axs[2].scatter(np.log10((full_point_sources['Flux_OI_6363'])/full_point_sources['Flux_Ha_6562']),
               np.log10(full_point_sources['Flux_OIII_5006']/full_point_sources['Flux_Hb_4861']),
               marker='.', s=4, color='gray', alpha=0.25, label='CSC Point Sources')
axs[2].scatter(np.log10((agostino_s2['Flux_OI_6363'])/agostino_s2['Flux_Ha_6562']),
               np.log10(agostino_s2['Flux_OIII_5006']/agostino_s2['Flux_Hb_4861']),
               marker='.', s=4, c='blue', label='Agostino', alpha=0.5)
axs[2].scatter(np.log10((portsmouth_s2['Flux_OI_6363'])/portsmouth_s2['Flux_Ha_6562']),
               np.log10(portsmouth_s2['Flux_OIII_5006']/portsmouth_s2['Flux_Hb_4861']),
               marker='.', s=4, c='red', label='Portsmouth', alpha=0.5)
axs[2].scatter(np.log10((full_min_abs['Flux_OI_6363'])/full_min_abs['Flux_Ha_6562']),
               np.log10(full_min_abs['Flux_OIII_5006_x']/full_min_abs['Flux_Hb_4861']),
               marker='*', s=8, color='black', alpha=1, label='Min Abs AGN Candidates')
axs[2].plot(kxOI, ke01OI, color='black', linestyle='dashed', label='Maximum Starburst')
axs[2].plot(slxOI, slOI, color='black', linestyle='-.', label='Seyfert-LINER')
axs[2].set_xlabel("log([OI]λ6363/Hα)", fontsize=14)
axs[2].set_xlim(-3, 0.75)
axs[2].set_ylim(-2,2.5)
axs[2].legend(loc='lower left')

plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/min_abs_bpt_v2.pdf", format="pdf")
plt.show()