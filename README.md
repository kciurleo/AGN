# AGN
This repository collects code relevant to my master's research on True Seyfert 2 AGN

### py

`sample_identification.py` uses the CSC/SDSS 2.1 crossmatch, along with the Portsmouth SDSS table and Agostino et al table to identify Seyfert AGN.

`bpt.py` makes BPT diagrams for the sample.

`useful_functions.py` contains functions used across the repository.

### sh

`find_obsid_given_name.sh` takes in a file with IAU names, then spits out a new file with the chandra OBSIDs (and dates and lengths/times) for those objects.

### Other Folders

`queries` contains various SQL/POST queries for crossmatching with SDSS.

`csvs` contains relevant csvs, vot tables, and txt files not tracked to GitHub for filesize reasons. Note to self: link where I downloaded all relevant csvs, and potentially track the small ones.

`plots` contains output plots.

`unorganized` contains code that is either in progress or yet to be sorted.