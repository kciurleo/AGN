# AGN
This repository collects code relevant to my master's research on True Seyfert 2 AGN

### py

`sample_identification.py` uses the CSC/SDSS 2.1 crossmatch, along with the Portsmouth SDSS table and Agostino et al table to identify Seyfert AGN.

`check_for_data.py` checks a given directory for downloaded Chandra data, for a file with Chandra obsids.

`get_upper_limits.py` queries eROSITA for the upper limits associated with a given position, for a file containing RA/dec.

`useful_functions.py` contains functions used across the repository.

`bpt.py` makes BPT diagrams of the CSC2.1 targets, along with Seyfert candidates.

`targetmap.py` makes a map of the CSC2.1 targets, along with Seyfert candidates.

### sh

`find_obsid_given_name.sh` takes in a file with IAU names, then spits out a new file with the chandra OBSIDs (and dates and lengths/times) for those objects.

`download_obsid.sh` downloads data with a 5m wait in between downloads for a list of Chandra obsids, given a list of obsids and start/finish indices.

`download_SDSS.sh` downloads associated SDSS spectra, trying for a full download first before looking for the legacy spectra. It currently doesn't work and creates an index of the entire SDSS archive; will need to rewrite. Do not run, and if index.html ends up staying opened, restarting the computer should work.

`move_dir.sh` and `move_dir_multiple.sh` take in a file with obsid names, then move them from one directory to another, given they exist. The latter checks multiple directories for the given obsid names.

`post_async.sh` makes an asynchronous request to a catalogue with the query in a given text file; initially set up for the XMM EPIC catalogue, and should in theory work for eROSITA, but currently doesn't.

### csvs
`CSC2.1p_OIR_SDSSspecmatch` is the [Chandra CSC2.1 Crossmatch](https://cxc.cfa.harvard.edu/csc/csc_crossmatches.html), downloaded as csv from linked.

`oldXmatch.csv` is the [Chandra CSC2.0 Crossmatch](https://cxc.cfa.harvard.edu/csc/csc_crossmatches.html), also downloaded as csv from the same linked location.

`4XMM_DR13cat_v1.0.csv` is the [XMM-Newton Serendipitous Source Catalog](https://www.cosmos.esa.int/web/xmm-newton/xsa), downloaded as csv from linked. Note this file is 3 GB and should only be downloaded if necessary; otherwise, query XMM as above for more manageable data.

`point_sources.csv` is a subset of the CSC2.1 crossmatch which identifies point sources and is used as a reference in the CasJobs queries.

`point_sources_classified_lines.csv` is the result of a CasJobs query `portsmouth_query.txt` retrieving line fluxes and BPT classifications from the Portsmouth table.

`agostino2021_table1.csv` is the [Agostino classifications](https://salims.pages.iu.edu/agn/) of SDSS AGN, downloaded as csv from linked.

`agostino_specIDS.csv` is the result of a CasJobs query `agostino_query.txt` matching SDSS specobjID and objID for Agostino Seyferts.

`full_point_sources.csv` is a subset of the CSC2.1 crossmatch which contains all the CSC2.1 data, as well as Agostino, Portsmouth, and direct XMM crossmatch data if available for each source. This is created in `sample_identification.py`.

`seyferts.csv` and `seyferts.vot` are identical subsets of `full_point_sources.csv` made up of any sources classified as a Seyfert by either Agostino or Portsmouth. The latter contains only a select few of the columns of the former.

`obsids_seyferts.csv` is a table of all Chandra obsids which contain sources identified as potential Seyferts, along with the observations' dates and exposure lengths, and is merged with `seyferts.csv` such that each source-obsid pair is listed once. This is created in `find_obsid_given_name.sh`.

`source_info_obsid_unique_seth.txt` is a table of Seyfert candidates previously identified by Seth Larner which were a useful comparison to Seyfert candidates identified in `seyferts.csv`.

`haves.txt` and `havenots.txt` are lists of obsids Seth Larner had previous downloaded and those needed to be downloaded; not extremely useful, but perhaps a consideration depending on if data is reprocessed or not.

`spidersros.xml` and `spidersxmm.xml` are tables resulting from queries to the associated SPIDERS (SPectroscopic IDentification of eROSITA Sources) [ROSAT](https://heasarc.gsfc.nasa.gov/db-perl/W3Browse/w3table.pl?tablehead=name%3Dspidersros&Action=More+Options) and [XMM](https://heasarc.gsfc.nasa.gov/db-perl/W3Browse/w3table.pl?tablehead=name%3Dspidersxmm&Action=More+Options) catalogs respectively, used to try to find more Seyfert candidates. In both cases, the whole catalog was downloaded as csv from linked by applying no query terms and setting the limit to "No limit."

`SDSS.txt` is a list of SDSS files to batch download.

`topcat_erosita.csv` is the result of a TOPCAT cone search of eROSITA around the candidates in `seyferts.vot`, with a search radius of 2".

`upper_limits.vot` is the result of the query in `get_upper_limits.py`, to retrieve upper limits for candidates in eROSITA's footprint.

`XMM_query_result.vot` is the downloaded result of the cone search of XMM around the candidates described by `post_async.sh`, with a search radius of 10".

### Other Folders

`queries` contains various SQL queries for crossmatching with SDSS and XMM.

`plots` contains output plots and figures.

`unorganized` contains code that is either in progress or yet to be sorted.
