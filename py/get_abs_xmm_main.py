from sherpa.astro.ui import *
import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import pandas as pd
import glob

#Main data directory
dir="/opt/pwdata/katie/xmm"

#Input file
input=pd.read_csv(f'{dir}/xmm_download_output.csv')
#only take the ones that didn't error on download
input = input.loc[input['download error']==False]

#define functions
def agreement(value1, errors1, value2, errors2):
    '''
    takes in two values and their associated errors array
    (upper and lower) and uses the maximum magnitude error
    (because I don't trust some of this) to check if errors
    overlap
    '''
    try:
        errors1 = np.asarray(errors1, dtype=float)
        errors2 = np.asarray(errors2, dtype=float)
        lower_bound1 = value1 - np.nanmax(np.abs(errors1[~np.isnan(errors1)]))
        upper_bound1 = value1 + np.nanmax(np.abs(errors1[~np.isnan(errors1)]))
        lower_bound2 = value2 - np.nanmax(np.abs(errors2[~np.isnan(errors2)]))
        upper_bound2 = value2 + np.nanmax(np.abs(errors2[~np.isnan(errors2)]))

        if upper_bound1 < lower_bound2 or upper_bound2 < lower_bound1:
            return False  
        else:
            return True
    except:
        #error with the errors haha
        return 'ERROR'

#model
mdl = f'(xsphabs.abs1*xszphabs.abs2 * xszpowerlw.p1)'

#arrays to add the values to
xmm_nH = []
xmm_nH_error_up = []
xmm_nH_error_down = []
xmm_gamma = []
xmm_gamma_up = []
xmm_gamma_down = []
nH_agrees = []
gamma_agrees = []

funabss=[]
f210s=[]
fsofts=[]
fmeds=[]
fhards=[]
fsums=[]

#Iterate over each row and do the fitting
for id, row in input.iterrows():
    nH=row['galactic nH']
    z=row['Z']
    obsid=str(row['observation_id']).zfill(10)
  
    filename = glob.glob(f'{dir}/{obsid}/pps/*SRSPEC{row["actual src_num"]}.FTZ')[0]

    clean()

    #stats are chi squared with a 3 sigma error and units of eV
    set_stat('chi2datavar')
    set_conf_opt("sigma", 3)

    #load in file, ignore outer limits, subtract the background, set model
    load_pha(f'{filename}')
    ignore()
    notice(0.35,10)
    subtract()
    set_model(1,mdl)

    #freeze galactic nH, set redshifts
    abs1.nH = nH
    freeze(abs1.nH)
    p1.redshift = z
    abs2.redshift = z
    fit()

    #Plotting
    plt.figure()
    plot_fit(xlog=True, ylog=True) 
    plot_model_component(p1, overplot=True) 
    plt.savefig(f'{dir}/{obsid}/pps/sherpa_fit_xmm.pdf')

    #residuals
    plt.figure()
    plot_resid(xlog=True, ylog=True)
    plt.savefig(f'{dir}/{obsid}/pps/sherpa_fit_resid_xmm.pdf')

    #Get errors
    conf()
    res = get_conf_results()

    #nH
    int_nH = res.parvals[res.parnames.index('abs2.nH')]
    int_nH_error_up = res.parmaxes[res.parnames.index('abs2.nH')]
    int_nH_error_down = res.parmins[res.parnames.index('abs2.nH')]

    #gamma
    gamma = res.parvals[res.parnames.index('p1.PhoIndex')]
    gamma_error_up = res.parmaxes[res.parnames.index('p1.PhoIndex')]
    gamma_error_down = res.parmins[res.parnames.index('p1.PhoIndex')]

    #flux calculations, need to edit
    #get energy in keV
    set_analysis('energy')

    #include the model to get unabsorbed flux; if we want absorbed, let it be none
    funabs=calc_energy_flux(0.3, 7.5, model=p1)
    f210=calc_energy_flux(2, 10, model=p1)

    #erosita bands
    fsoft=calc_energy_flux(0.2, 0.6, model=p1)
    fmed=calc_energy_flux(0.6, 2.3, model=p1)
    fhard=calc_energy_flux(2.3, 5, model=p1)
    fsum=calc_energy_flux(0.2, 5, model=p1)

    #compare to chandra bere
    gamma_agree = 'ERROR'
    nH_agree = 'ERROR'

    gamma_agree = agreement(gamma, [gamma_error_up,gamma_error_down], row['gamma'], row[['gamma error plus', 'gamma error minus']])
    nH_agree = agreement(int_nH, [int_nH_error_up,int_nH_error_down], row['nH'], row[['nH error plus', 'nH error minus']])

    #write out a text file with the info
    variables = {
    'xmm nH': int_nH,
    'xmm nH error plus': int_nH_error_up,
    'xmm nH error minus': int_nH_error_down,
    'xmm gamma': gamma,
    'xmm gamma error plus': gamma_error_up,
    'xmm gamma error minus': gamma_error_down,
    'nH agrees': nH_agree,
    'gamma agrees': gamma_agree,
    'xmm flux': funabs,
    'xmm 2-10 flux': f210,
    'xmm soft flux': fsoft,
    'xmm med flux': fmed,
    'xmm hard flux': fhard,
    'xmm soft flux': fsum
    }

    # Specify the file name
    file_name = f'{dir}/{obsid}/pps/sherpa_output.txt'

    # Write to the text file
    with open(file_name, 'w') as f:
        for var_name, var_values in variables.items():
            f.write(f"{var_name}: {var_values}\n")

    #save the values in the df
    xmm_nH.append(int_nH)
    xmm_nH_error_up.append(int_nH_error_up)
    xmm_nH_error_down.append(int_nH_error_down)
    xmm_gamma.append(gamma)
    xmm_gamma_up.append(gamma_error_up)
    xmm_gamma_down.append(gamma_error_down)
    nH_agrees.append(nH_agree)
    gamma_agrees.append(gamma_agree)
    
    funabss.append(funabs)
    f210s.append(f210)
    fsofts.append(fsoft)
    fmeds.append(fmed)
    fhards.append(fhard)
    fsums.append(fsum)

    #write the other values too

#add all the new columns
input['xmm nH'] = xmm_nH
input['xmm nH error plus'] = xmm_nH_error_up
input['xmm nH error minus'] = xmm_nH_error_down
input['xmm gamma'] = xmm_gamma
input['xmm gamma plus'] = xmm_gamma_up
input['xmm gamma minus'] = xmm_gamma_down

input['xmm flux']=funabss
input['xmm flux 2-10']=f210s
input['xmm soft flux']=fsofts
input['xmm med flux']=fmeds
input['xmm hard flux']=fhards
input['xmm sum flux']=fsums

input['gamma agree'] = gamma_agrees
input['nH agree'] = nH_agrees

input.to_csv(f'{dir}/xmm_sherpa_out.csv', index=False)

print(len(input.loc[input['nH agree']==False]))
print(len(input.loc[input['gamma agree']==False]))