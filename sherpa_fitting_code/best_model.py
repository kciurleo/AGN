import numpy as np
from os import path
from os import listdir
import sys
import pandas as pd
from matplotlib import pyplot as plt

####################
#Defining functions

def read_doc_simple(file_path):
    with open(file_path,'r') as file:
        data_list = file.read().split('\n')

    cstat = data_list[1]
    gamma = data_list[7]

    try:
        return float(cstat), float(gamma)
    except:
        return cstat,gamma

def triply_unabsorbed(outroot, obsids):
    #For a list of obsids, return a list of those unabsorbed in all three models

    unabsorbed_array=[]

    for obsid in obsids:

        main_path = f'{outroot}/min_abs/{obsid}/{obsid}_abs_summary.txt'
        alt_path = f'{outroot}/min_abs_alt/{obsid}/{obsid}_abs_summary.txt'
        res_path = f'{outroot}/min_abs_res/{obsid}/{obsid}_abs_summary.txt'

        if path.exists(main_path) and path.exists(res_path) and path.exists(alt_path):
            unabsorbed_array.append(obsid)
            
    return unabsorbed_array
    
def get_triply_unabsorbed(outroot):
    #Find all subdirectories in minimally absorbed directories, excluding loose files
    models = ['','_alt', '_res']
    min_abs_potential_list = []

    for model in models:
        dirs = listdir(f'{outroot}/min_abs{model}')
        for direc in dirs:
            if path.isdir(f'{outroot}/min_abs/{direc}'):
                min_abs_potential_list.append(direc)
    
    #Get unique list of potential triply absorbed 
    min_abs_potential_list=set(min_abs_potential_list)

    #Check which are absorbed in all three
    unabsorbed_list = triply_unabsorbed(outroot, min_abs_potential_list)
    
    return unabsorbed_list

def get_best_model(data_dir, outroot, obsids):
    #Determine which fit is the best for a given obsid; iterate over all list

    best_models = []

    #Find 3 sigma cutoff for main vs alt fit
    main = pd.read_csv(f'{outroot}/allinfo_full_withratio.csv')
    alt = pd.read_csv(f'{outroot}/allinfo_full_withratio_alt.csv')
    mean=np.mean(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'))
    std_dev = np.std(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'))

    cutoff = mean + 3 * std_dev

    for obsid in obsids:
        file = f'{data_dir}/{obsid}/primary/sherpaout.txt'
        alt_file = f'{data_dir}/{obsid}/primary/sherpaout_alt.txt'
        res_file = f'{data_dir}/{obsid}/primary/sherpaout_restricted.txt'

        try:
            stat,gamma = read_doc_simple(file)
        except (FileNotFoundError, IndexError):
            stat,gamma = ('ERROR','ERROR')
        try:
            stat_res,gamma_res = read_doc_simple(res_file)
        except (FileNotFoundError, IndexError):
            stat_res,gamma_res = ('ERROR','ERROR')
        try:
            stat_alt,gamma_alt = read_doc_simple(alt_file)
        except (FileNotFoundError, IndexError):
            stat_alt,gamma_alt = ('ERROR','ERROR')
        
        #Return error if all stats are error
        if stat == 'ERROR' and stat_alt == 'ERROR' and stat_res == 'ERROR':
            best_models.append('ERROR')

        #If alt model has better stat than main, then pick that
        elif stat_alt != 'ERROR' and stat != 'ERROR' and stat - stat_alt > cutoff:
            best_models.append('alt')

        #Else if main model's slope is physical, then pick that
        elif gamma != 'ERROR' and gamma < 2.2 and gamma > 1.5:
            best_models.append('main')

        #Otherwise, return restricted, provided there's no error
        elif gamma_res != 'ERROR':
            best_models.append('res')
            #There might still be an error with the statistic

        #Just in case
        else:
            best_models.append('ERROR')

    return best_models

def is_best_unabsorbed(outroot, obsids, models):
    #Checks to see if an array of obsids is unabsorbed for a given array of models
    best_unabsorbed_array=[]

    for i, obsid in enumerate(obsids):
        if models[i] == 'alt':
            ending = '_alt'
        elif models[i] == 'res':
            ending = '_res'
        else:
            ending = ''

        unabsorbed_path = f'{outroot}/min_abs{ending}/{obsid}/{obsid}_abs_summary.txt'

        if path.exists(unabsorbed_path):
            best_unabsorbed_array.append(True)
        else:
            best_unabsorbed_array.append(False)
            
    return best_unabsorbed_array


def make_histograms(outroot, cstat_bins, del_cstat_bins):
    #Makes some histograms of cstats for model cutoff purposes
    main = pd.read_csv(f'{outroot}/allinfo_full_withratio.csv')
    alt = pd.read_csv(f'{outroot}/allinfo_full_withratio_alt.csv')
    res = pd.read_csv(f'{outroot}/allinfo_full_withratio_res.csv')
    final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')


    alt=final_full.loc[final_full['model']=='alt']

    new_main=main.loc[~main['CXO name'].isin(alt['CXO name'])]

    plt.figure(figsize=(8,8))
    plt.hist(pd.to_numeric(new_main['gamma'], errors='coerce'), bins=100)
    plt.axvline(1.7, color='black')
    plt.axvline(2.2, color='black')
    plt.xlabel('Gamma')
    plt.show()
    '''
    interesting_guys=new_main.loc[(new_main['gamma']!='ERROR')]
    interesting_guys=interesting_guys.loc[(interesting_guys['gamma'].astype(float)>1.5) & (interesting_guys['gamma'].astype(float)<2.2)]

    print('mean: ',np.nanmean(interesting_guys['gamma error plus'].astype(float)))
    print('median: ',np.nanmedian(interesting_guys['gamma error plus'].astype(float)))
    print('std: ',np.std(interesting_guys['gamma error plus'].astype(float)))

    plt.figure(figsize=(8,8))
    plt.hist(interesting_guys['gamma error plus'].astype(float), bins=40)
    plt.xlabel('Gamma error')
    plt.show()
    '''
    '''
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(10,10))

    ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

    ax1.hist(pd.to_numeric(main['Cstat'], errors='coerce'), bins = cstat_bins)
    ax1.set_ylabel('Main')
    ax1.set_xlabel('Cstat')

    ax2.hist(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'), bins = del_cstat_bins)
    ax2.set_ylabel('Main-Alt')
    ax2.set_xlabel('del Cstat')

    ax3.hist(pd.to_numeric(alt['Cstat'], errors='coerce'), bins = cstat_bins)
    ax3.set_ylabel('Alt')
    ax3.set_xlabel('Cstat')

    ax4.hist(pd.to_numeric(res['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'), bins = del_cstat_bins)
    ax4.set_ylabel('Restricted-Alt')
    ax4.set_xlabel('del Cstat')

    ax5.hist(pd.to_numeric(res['Cstat'], errors='coerce'), bins = cstat_bins)
    ax5.set_ylabel('Restricted')
    ax5.set_xlabel('Cstat')

    ax6.hist(pd.to_numeric(res['Cstat'], errors='coerce')-pd.to_numeric(main['Cstat'], errors='coerce'), bins = del_cstat_bins)
    ax6.set_ylabel('Restricted-Main')
    ax6.set_xlabel('del Cstat')

    #plt.savefig(f'{outroot}/cstat_histograms.pdf', format='pdf')
    plt.show()

    #Extra stuff to describe later
    mean=np.mean(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'))
    std_dev = np.std(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'))
    print(mean)
    print(mean+3*std_dev)

    plt.figure(figsize=(8,6))
    plt.hist(pd.to_numeric(main['Cstat'], errors='coerce')-pd.to_numeric(alt['Cstat'], errors='coerce'), bins = del_cstat_bins*3)
    plt.ylabel('Main-Alt')
    plt.xlabel('del Cstat')
    plt.xlim(-20,20)
    plt.show()
    '''

def diagnose_best_fit(outroot):
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
        except Exception as e:
            print(f"Error type: {type(e).__name__}, Message: {e}")
    
    main = pd.read_csv(f'{outroot}/allinfo_full_withratio.csv')
    alt = pd.read_csv(f'{outroot}/allinfo_full_withratio_alt.csv')
    res = pd.read_csv(f'{outroot}/allinfo_full_withratio_res.csv')
    final_full = pd.read_csv('/opt/pwdata/katie/csc2.1/final_data/final_info_full.csv')


    alt=final_full.loc[final_full['model']=='alt']

    new_main=main.loc[~main['CXO name'].isin(alt['CXO name'])]
    
    T=0
    F=0
    Errors=0
    sucked=0
    trues = []

    for id, row in new_main.iterrows():
        print(id)
        errors=[]
        try:
            errors.append(float(row['gamma error plus']))
        except:
            pass
        try:
            errors.append(float(['gamma error minus']))
        except:
            pass
        if len(errors)>0:
            print(errors)
            print(row['gamma error minus'])
            agree=agreement(1.95, [0.25], float(row['gamma']), errors)
        else:
            agree='ERROR'
            sucked+=1

        if agree=='ERROR':
            print(errors)
            Errors+=1
        elif agree==True:
            T+=1
            trues.append(row['# ObsID'])
        else:
            F+=1
    print(f'True: {T}, False: {F}, Errors: {Errors}, sucked {sucked}')

    T1=0
    F1=0
    Errors1=0
    sucked1=0
    trues1 = []

    for id, row in new_main.iterrows():
        print(id)
        errors=[]
        try:
            errors.append(float(row['gamma error plus']))
        except:
            pass
        try:
            errors.append(float(['gamma error minus']))
        except:
            pass
        if len(errors)>0:
            print(errors)
            print(row['gamma error minus'])
            agree=agreement(1.9, [0], float(row['gamma']), errors)
        else:
            agree='ERROR'
            sucked1+=1

        if agree=='ERROR':
            print(errors)
            Errors1+=1
        elif agree==True:
            T1+=1
            trues1.append(row['# ObsID'])
        else:
            F1+=1
    print(f'True: {T1}, False: {F1}, Errors: {Errors1}, sucked {sucked1}')


    interesting_guys=new_main.loc[(new_main['gamma']=='ERROR')]
    print(len(interesting_guys['gamma']))
    print(trues)
    basicagreementdudes=main.loc[main['# ObsID'].isin(trues1)]
    agreementdudes=main.loc[main['# ObsID'].isin(trues)]

    plt.figure(figsize=(10,6))
    plt.hist(pd.to_numeric(new_main['gamma'], errors='coerce'), bins=100, label='All Main Fits')
    plt.hist(pd.to_numeric(agreementdudes['gamma'], errors='coerce'), bins=100, label='Errors agree with 1.9')
    plt.hist(pd.to_numeric(basicagreementdudes['gamma'], errors='coerce'), bins=100, alpha=0.5, label='Errors agree with 1.7-2.2')
    plt.axvline(1.7, color='black', label='Original cutoff (1.7-2.2)')
    plt.axvline(2.2, color='black')
    plt.axvline(1.5, color='black', linestyle='dashed', label='Current cutoff (1.5-2.2)')
    plt.xlabel('Gamma')
    plt.legend()
    plt.title('Main fit gamma, Bins=100')
    plt.savefig('/Users/kciurleo/Documents/kciurleo/AGN/plots/histogram_gamma_main.pdf', format="pdf")
    plt.show()

if __name__ == '__main__':
    outroot='/opt/pwdata/katie/csc2.1/'
    diagnose_best_fit(outroot)