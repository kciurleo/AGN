import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

targets = pd.read_csv("/Volumes/galaxies/Seth/AGNs/x-ray/final_data/all_info_final.csv")

counts = targets['Count rate (/s)']*targets['Chandra Exposure (ks)']*1000

#Histogram of counts of Seth's targets
'''
fig, axs = plt.subplots(1, 2, figsize=(16, 6))

axs[0].hist(counts, bins=100)
axs[0].set_xlabel("Chandra Counts, full range")
axs[0].set_ylabel("Log Number of Sources")
axs[0].set_title("Seth's Sources, 100 bins")
axs[0].set_yscale('log')


axs[1].hist(counts, bins=600)
axs[1].set_xlim(0,2000)
axs[1].set_xlabel("Chandra Counts, lower end")
axs[1].set_ylabel("Number of Sources")
axs[1].set_title("Seth's Sources, 600 bins")
plt.tight_layout()

plt.show(block=False)
'''
'''
reasonable_targets=targets.loc[(targets['Fx/FOIII']<10) & (targets['Fx/FOIII']>0)]

fig, axs = plt.subplots(1, 2, figsize=(16, 6))

axs[0].hist(reasonable_targets['Fx/FOIII'], bins=30)
axs[0].set_xlabel("F_x/F_[OIII]")
axs[0].set_ylabel("Number of Sources")
axs[0].set_title("Seth's Sources, 30 bins")


axs[1].hist(reasonable_targets['Fx/FOIII error'], bins=30)
axs[1].set_xlabel("F_x/F_[OIII] error")
axs[1].set_ylabel("Number of Sources")
axs[1].set_title("Seth's Sources, 30 bins")
plt.tight_layout()

plt.show()
'''
'''
reasonable_targets=targets.loc[(targets['Fx/FOIII']<10) & (targets['Fx/FOIII']>0)]

fig, axs = plt.subplots(1, 2, figsize=(16, 6))

axs[0].hist(targets['Fx/FOIII'], bins=300)
axs[0].set_xlabel("F_x/F_[OIII]")
axs[0].set_ylabel("Number of Sources")
axs[0].set_title("Seth's Sources, 300 bins")


axs[1].hist(targets['Fx/FOIII error'], bins=300)
axs[1].set_xlabel("F_x/F_[OIII] error")
axs[1].set_ylabel("Number of Sources")
axs[1].set_title("Seth's Sources, 300 bins")
plt.tight_layout()

plt.show()

'''
nonzero = targets.loc[targets['OIII5007 flux'] != -1.000000e-17]

print(len(nonzero['OIII5007 flux']))
print(len(targets['Chandra Exposure (ks)']))

print(np.min(nonzero['OIII5007 flux']))