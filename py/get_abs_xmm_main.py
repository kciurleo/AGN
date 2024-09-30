from sherpa.astro.ui import *
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import pandas as pd
import glob

#Input file
input=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/xmm_download_output.csv')
#only take the ones that didn't error on download
input = input.loc[input['download error']==False]

#Main data directory
dir="/opt/pwdata/katie/xmm"

#model
mdl = f'(xsphabs.abs1*xszphabs.abs2 * xszpowerlw.p1)'

#Iterate over each row and do the fitting
for id, row in input.head(2).iterrows:
    nH=row['galactic nH']
    z=row['Z']
    obsid=str(row['observation_id']).zfill(10)
    filename = glob.glob(f'{obsid}/pps/*SRSPEC{row['actual src_num']}.FTZ')

    clean()
    load_pha(f'{dir}/{filename}')
    ignore()
    notice(0.3,10)
    #actual fitting
    set_model(1,mdl)

    abs1.nH = nH
    freeze(abs1.nH)
    p1.redshift = z
    abs2.redshift = z
    fit()
    plot_fit_resid(xlog=True,ylog=True)

    #make a plot
    plot_fit_resid(xlog=True,ylog=True)
    plt.title(None)
    plt.savefig(f'{dir}/{obsid}/pps/sherpa_main_fit.pdf')
    plt.close()

    #KATIE you'll want to get chi squared statistics somewhere over here

    #get par values
    local_nH = abs2.nH.val
    xmm_gamma = p1.PhoIndex.val

    #pretty sure this freezes the above as well
    for p in get_model().pars:
        p.freeze()

    #KATIE you don't know how this flux calculation thing works in Seth's code.
    #rectify that and do so here.

    #KATIE save a file with relevant information

#KATIE write a csv that has all the fluxes etc