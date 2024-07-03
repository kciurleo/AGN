#This script will fit the dually absorbed power law model to the sources
#Using sherpa and the BXA emperical background modelimport matplotlib.pyplot as plt
from sherpa.astro.ui import *
import sys
import numpy as np
import matplotlib.pyplot as plt
from bxa.sherpa.background.models import ChandraBackground
from bxa.sherpa.background.fitters import SingleFitter
from sherpa.astro import xspec
from run_stat_test_fp import calc_cstat
import os
import time

def get_abs_alt(nH,z,dir):
    clean()

    #load the sci data
    load_pha(1,f'{dir}/reextract_pha.pi')
    load_bkg_rmf(f'{dir}/reextract_pha_bkg.rmf')
    load_bkg_arf(f'{dir}/reextract_pha_bkg.arf')

    set_stat('cstat')
    set_analysis(1,'energy')

    #define the science mode
    mdl = f'(xsphabs.abs1 * (xszpowerlw.p1 + xszphabs.abs2 * xszpowerlw.p2))'
    set_model(1,mdl)

    abs1.nH = nH
    freeze(abs1.nH)
    p2.redshift = z
    abs2.redshift = z
    link(p1.PhoIndex, p2.PhoIndex)



    #Use the fitter to stage the background so it can be fit by sherpa
    fitter = SingleFitter(1,f'{dir}/reextract_pha_bkg.pi',ChandraBackground)

    #cannot use the built in fitter staging method since that fucks up the energy units on the plots
    for stage in fitter.bm.stages:
        fitter.prepare_stage(stage=stage)

    #ignore low and high energy
    ignore()
    notice(0.3,7.5)
    ignore(bkg_id=1)
    notice(0.3,7.5,bkg_id=1)

    #perform the bkg fit
    fit_bkg()

    #freeze the background model parameters
    for p in get_bkg_model(1).pars:
        p.freeze()

    #set the full model
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdl))

    #sherpa fit
    fit()



    #make a plot
    plot_fit_resid(xlog=True,ylog=True)
    plt.title(None)
    plt.savefig(f'{dir}/sherpa_data_fit_alt.pdf')
    plt.close()

    #get the value of cstat
    calc_stat_info()
    stat_info = get_stat_info()[2]
    cstat = stat_info.statval
    dof = stat_info.dof

    set_analysis(1,'energy','counts')
    plot_fit(xlog=True,ylog=True)

    try:
        stat, Ce, Cv = calc_cstat(cstat)
    except:
        stat = 'ERROR'
        Ce = 'ERROR'
        Cv = 'ERROR'


    #create the output document
    #format the same as the xspec one so it can be read same

    #calculate covariance to get par errors
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_errors = covar[10].strip('parmaxes     = (').rstrip(')').split(',')
    lower_errors = covar[9].strip('parmins     = (').rstrip(')').split(',')
    #the error tuples are in the order +,-
    nH_errors = (upper_errors[0],lower_errors[0])
    #format the errors to match the output document reqiurements
    nH_err = f'{nH_errors[1]} {nH_errors[0]}'
    gamma_errors = (upper_errors[1],lower_errors[1])
    gamma_err = f'{gamma_errors[1]} {gamma_errors[0]}'
    norm_errors = (upper_errors[2],lower_errors[2])
    norm_err = f'{norm_errors[1]} {norm_errors[0]}'

    #get par values
    local_nH = abs2.nH.val
    gamma = p1.PhoIndex.val



    #calculate the fluxes
    #now fix the source model and add in the flux calculating models
    for p in get_model().pars:
        p.freeze()

    #0.3 to 7.5 KeV flux
    mdlx = f'xscflux.fx({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdlx))
    fx.Emin = 0.3
    fx.Emax = 7.5

    fit()
    #get value and covar of fx
    Xflux_value = 10**(fx.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    Xflux_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - Xflux_value)
    Xflux_error_minus = abs(Xflux_value - (10 **  (fx.lg10Flux.val - float(lower_error))))

    #2 to 10 KeV flux
    mdl210 = f'xscflux.f210({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdl210))
    f210.Emin = 2.0
    f210.Emax = 10.0

    fit()
    #get value and covar of f210
    flux210_value = 10**(f210.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    flux210_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - flux210_value)
    flux210_error_minus = abs(flux210_value - (10 **  (fx.lg10Flux.val - float(lower_error))))




    #for now, dummy values
    Xflux= f"{Xflux_value} {Xflux_error_plus} {Xflux_error_minus}"
    flux_210 = f"{flux210_value} {flux210_error_plus} {flux210_error_minus}"


    #Format the string that will be written to the file
    out = f'#CSTAT:\n{cstat}\nnH:\n{local_nH}\nERROR:\n{nH_err}\nGamma:\n{gamma}\nERROR:\n{gamma_err}\n0.3-7.5 Flux:\n{Xflux}\n2-10 Flux:\n{flux_210}\nTest statistic:\n{stat}\nCe:\n{Ce}\nCv:\n{Cv}\ndof:\n{dof}'

    #save the session
    save(filename=f'{dir}/get_abs_alt.save', clobber=True)

    #write out
    with open(f'{dir}/sherpaout_alt.txt','w') as outdoc:
        outdoc.write(out)


    return

if __name__ == '__main__':
    #get_abs(0.0375,0.22018880,'../x-ray/all_sources_copy/3130/primary')
    get_abs_alt(0.00912,0.1290917,'../x-ray/all_sources_copy/4259/primary')
    os.system('open ../x-ray/all_sources_copy/19563/primary/sherpaout.txt')
