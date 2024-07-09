import pandas as pd
import matplotlib.pyplot as plt

targets = pd.read_csv("/Volumes/galaxies/Seth/AGNs/x-ray/final_data/all_info_final.csv")


counts = targets['Count rate (/s)']*targets['Chandra Exposure (ks)']*1000

#Histogram of counts of Seth's targets
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

plt.show()