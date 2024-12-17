#This script will fit the dually absorbed power law model to the sources
#Using sherpa and the BXA emperical background model
#Power law slope fixed to the canonical range
import matplotlib.pyplot as plt
from sherpa.astro.ui import *
import sys
import numpy as np
import matplotlib.pyplot as plt
from bxa.sherpa.background.models import ChandraBackground
from bxa.sherpa.background.fitters import SingleFitter
import os

def get_abs_restricted(nH,z,dir):
    clean()

    #load the sci data
    load_pha(1,f'{dir}/reextract_pha.pi')
    load_bkg_rmf(f'{dir}/reextract_pha_bkg.rmf')
    load_bkg_arf(f'{dir}/reextract_pha_bkg.arf')

    set_stat('cstat')
    set_analysis(1,'energy')


    #define the science mode
    srcmodel = 'xszpowerlw.p1'
    absmodel = 'xsphabs.abs1*xszphabs.abs2'
    mdl = f'({absmodel} * {srcmodel})'
    set_model(1,mdl)

    #set known pars
    abs1.nH = nH
    freeze(abs1.nH)
    p1.PhoIndex = 1.9
    freeze(p1.PhoIndex)

    p1.redshift = z
    abs2.redshift = z

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

    #save specifically for later plotting purposes
    save(filename=f'{dir}/plotting_get_abs_restricted.save', clobber=True)

    #make a plot
    plot_fit_resid(xlog=True,ylog=True)
    plt.title(None)
    plt.savefig(f'{dir}/sherpa_data_fit_restricted.pdf')
    plt.close()

    #Plotting
    plt.figure()
    plot_fit(xlog=True, ylog=True) 
    plot_model_component(p1, overplot=True, label='Constant Power Law') 
    plt.savefig(f'{dir}/katie_test_restricted.pdf')
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
    gamma_err = f'NA NA'
    norm_errors = (upper_errors[1],lower_errors[1])
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

#eROSITA 'soft' flux
    mdlsoft = f'xscflux.fsoft({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdlsoft))
    fsoft.Emin = 0.2
    fsoft.Emax = 0.6

    fit()
    #get value and covar of fsoft
    fluxsoft_value = 10**(fsoft.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    fluxsoft_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - fluxsoft_value)
    fluxsoft_error_minus = abs(fluxsoft_value - (10 **  (fx.lg10Flux.val - float(lower_error))))

    #eROSITA 'medium' flux
    mdlmed = f'xscflux.fmed({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdlmed))
    fmed.Emin = 0.6
    fmed.Emax = 2.3

    fit()
    #get value and covar of fmed
    fluxmed_value = 10**(fmed.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    fluxmed_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - fluxmed_value)
    fluxmed_error_minus = abs(fluxmed_value - (10 **  (fx.lg10Flux.val - float(lower_error))))

    #eROSITA 'hard' flux
    mdlhard = f'xscflux.fhard({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdlhard))
    fhard.Emin = 2.3
    fhard.Emax = 5.0

    fit()
    #get value and covar of fhard
    fluxhard_value = 10**(fhard.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    fluxhard_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - fluxhard_value)
    fluxhard_error_minus = abs(fluxhard_value - (10 **  (fx.lg10Flux.val - float(lower_error))))
    
    #eROSITA 'summed' flux
    mdlsum = f'xscflux.fsum({mdl})'
    set_full_model(1, get_bkg_model(1)*get_bkg_scale(1)+get_response(1)(mdlsum))
    fsum.Emin = 0.2
    fsum.Emax = 5.0

    fit()
    #get value and covar of fsoft
    fluxsum_value = 10**(fsum.lg10Flux.val)
    covariance()
    covar = get_covar_results()
    covar = str(covar).split('\n')
    upper_error = covar[10].strip('parmaxes     = (').rstrip(')').rstrip(',')
    lower_error = covar[9].strip('parmins     = (').rstrip(')').rstrip(',')
    fluxsum_error_plus = abs((10 **  (fx.lg10Flux.val + float(upper_error))) - fluxsum_value)
    fluxsum_error_minus = abs(fluxsum_value - (10 **  (fx.lg10Flux.val - float(lower_error))))

    #write out the fluxes
    Xflux= f"{Xflux_value} {Xflux_error_plus} {Xflux_error_minus}"
    flux_210 = f"{flux210_value} {flux210_error_plus} {flux210_error_minus}"
    flux_soft = f"{fluxsoft_value} {fluxsoft_error_plus} {fluxsoft_error_minus}"
    flux_med = f"{fluxmed_value} {fluxmed_error_plus} {fluxmed_error_minus}"
    flux_hard = f"{fluxhard_value} {fluxhard_error_plus} {fluxhard_error_minus}"
    flux_sum = f"{fluxsum_value} {fluxsum_error_plus} {fluxsum_error_minus}"


    #Format the string that will be written to the file
    out = f'#CSTAT:\n{cstat}\nnH:\n{local_nH}\nERROR:\n{nH_err}\nGamma:\n{gamma}\nERROR:\n{gamma_err}\n0.3-7.5 Flux:\n{Xflux}\n2-10 Flux:\n{flux_210}\nTest statistic:\n{stat}\nCe:\n{Ce}\nCv:\n{Cv}\ndof:\n{dof}\nSoft 0.2-0.6 Flux:\n{flux_soft}\nMedium 0.6-2.3 Flux:\n{flux_med}\nHard 2.3-5.0 Flux:\n{flux_hard}\nSummed 0.2-5 Flux:\n{flux_sum}'

    #save the session
    save(filename=f'{dir}/get_abs_restricted.save', clobber=True)

    #write out
    with open(f'{dir}/sherpaout_restricted.txt','w') as outdoc:
        outdoc.write(out)


    return

if __name__ == '__main__':
    get_abs_restricted(0.0375,0.22018880,'../x-ray/all_sources_copy/3130/primary')
