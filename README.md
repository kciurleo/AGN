# AGN
This repository collects code relevant to my master's research on True Seyfert 2 AGN

### py

`sample_identification.py` uses the CSC/SDSS 2.1 crossmatch, along with the Portsmouth SDSS table and Agostino et al table to identify Seyfert AGN.

`bpt.py` makes BPT diagrams for the sample.

`check_for_data.py` checks a given directory for downloaded Chandra data, for a file with Chandra obsids.

`useful_functions.py` contains functions used across the repository.

### sh

`find_obsid_given_name.sh` takes in a file with IAU names, then spits out a new file with the chandra OBSIDs (and dates and lengths/times) for those objects.

`move_dir.sh` takes in a file with obsid names, then moves them from one directory to another, given they exist.

### Other Folders

`queries` contains various SQL/POST queries for crossmatching with SDSS.

`csvs` contains relevant csvs, vot tables, and txt files not tracked to GitHub for filesize reasons. Note to self: link where I downloaded all relevant csvs, and potentially track the small ones.

`plots` contains output plots.

`unorganized` contains code that is either in progress or yet to be sorted.