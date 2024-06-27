#!/bin/sh

#This script downloads the full eBOSS, BOSS, and SEQUELS spectra (the coadded spectrum, the redshift and 
#classification fits, spectral line fits, and optionally the individual exposures which contributed to the coadd)
#from SDSS to a given directory for a given list of spectra. If it can't download from that, download from the
#SDSS legacy spectra.

#DONT RUN THIS CODE SOMETHING IS MAJORLY WRONG

spectra="/Users/kciurleo/Documents/kciurleo/AGN/csvs/SDSS.txt"
directory="/Volumes/galaxies/Katie/SDSS_data/"

cd "$directory"

#Try eBOSS
wget  -nv -r -nH --cut-dirs=7 \
-i "$spectra" \
-B "https://data.sdss.org/sas/dr17/eboss/spectro/redux/v5_13_2/spectra/full/"
