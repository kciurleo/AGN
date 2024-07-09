import os
import pandas as pd
import glob
import numpy as np

needed = pd.read_csv("/Volumes/galaxies/Seth/AGNs/x-ray/final_data/all_info_final.csv").head()

final_data = pd.DataFrame(columns=needed.columns)

obsids=needed['ObsID']

for i in range(len(obsids)):
    selected_row = needed.loc[needed['ObsID']==obsids[i]]
    selected_row.insert(0, 'model', 'testing')

    final_data = pd.concat([final_data, selected_row])


data_dir = '/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/data'

def read_doc(file_path):
    with open(file_path,'r') as file:
        data_list = file.read().split('\n')

    stat = data_list[15]
    gamma = data_list[7]

    try:
        return float(stat), float(gamma)
    except:
        return stat,gamma

def get_best_model(data_dir, obsids):
    #Determine which fit is the best for a given obsid; iterate over all list

    best_models = []

    for obsid in obsids:
        file = f'{data_dir}/{obsid}/primary/sherpaout.txt'
        alt_file = f'{data_dir}/{obsid}/primary/sherpaout_alt.txt'
        res_file = f'{data_dir}/{obsid}/primary/sherpaout_restricted.txt'

        try:
            stat,gamma = read_doc(file)
        except (FileNotFoundError, IndexError):
            stat,gamma = ('ERROR','ERROR')
        try:
            stat_res,gamma_res = read_doc(res_file)
        except (FileNotFoundError, IndexError):
            stat_res,gamma_res = ('ERROR','ERROR')
        try:
            stat_alt,gamma_alt = read_doc(alt_file)
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

        #Just in case
        else:
            best_models.append('ERROR')

    return best_models

#print(get_best_model(data_dir,['10561', '11469', '6129', '6128', '5929']))


seth = pd.read_csv("/Volumes/galaxies/Seth/AGNs/x-ray/final_data/all_info_final.csv")
def strip_letters(id_str):
    return ''.join(filter(str.isdigit, id_str))

# Apply function and convert to numeric
seth['ObsID'] = seth['ObsID'].apply(strip_letters)

seth.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/seth_full_list.csv', index=False)