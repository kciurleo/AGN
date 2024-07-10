import numpy as np
from os import path
from os import listdir
import sys

####################
#Defining functions

def read_doc_simple(file_path):
    with open(file_path,'r') as file:
        data_list = file.read().split('\n')

    stat = data_list[15]
    gamma = data_list[7]

    try:
        return float(stat), float(gamma)
    except:
        return stat,gamma

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

def get_best_model(data_dir, obsids):
    #Determine which fit is the best for a given obsid; iterate over all list

    best_models = []

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
        elif stat_alt != 'ERROR' and stat != 'ERROR' and stat - stat_alt>0.5:
            best_models.append('alt')

        #Else if main model's slope is physical, then pick that
        elif gamma != 'ERROR' and gamma < 2.2 and gamma > 1.7:
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



if __name__ == '__main__':

    data_dir = sys.argv[1]
    outroot = sys.argv[2]
    obsids = sys.argv[3]

    print(get_triply_unabsorbed(outroot))

    print(get_best_model(data_dir, obsids))