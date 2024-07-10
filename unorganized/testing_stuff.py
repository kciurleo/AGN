import os
import pandas as pd
import glob
import numpy as np
'''
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

#seth.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/seth_full_list.csv', index=False)

obs = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv')['CHANDRA_OBSID']

guys = os.listdir("/opt/pwdata/katie/csc2.1data")
guys_int=[]
for i in guys:
    guys_int.append(int(i))

def isindir(obj, dir):
    dudes = set(os.listdir(dir))

print(type(obs[0]),'and',type(guys_int[0]))
print(len(set(obs)-set(guys_int)))
unfound = list(set(obs)-set(guys_int))

with open('/Users/kciurleo/Documents/kciurleo/AGN/csvs/not_found_obsids.txt','w') as doc:
    doc.write("#This document contains obsids related to potential Seyfert candidates which aren't found on the archive site.")

    for item in unfound:
            doc.write(f'{item}\n')
'''

df=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv', dtype=str)
'''
names = ['2CXO J134736.4+173404','2CXO J131651.2+055647','2CXO J235720.1-005829','2CXO J104429.3+113810']

new_df = pd.DataFrame(columns=df.columns)

for name in names:
    row = df.loc[df['CSC21P_name'] == name].head(1)
    new_df = pd.concat([new_df, row],ignore_index=True)

additionalrow = df.loc[(df['CSC21P_name'] == '2CXO J135317.9+332929') & (df['CHANDRA_OBSID'] == '4867')]

new_df = pd.concat([new_df, additionalrow], ignore_index=True)
new_df.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/katie_testcoords.csv', index=False)
'''

print(np.min(df['Flux_OIII_5006']))

nonzero = df.loc[df['Flux_OIII_5006'] != '0.0' ]
print(len(df['Flux_OIII_5006']))
print(len(nonzero['Flux_OIII_5006']))
for i in range(len(set(nonzero['Flux_OIII_5006']))):
    print(list(set(nonzero['Flux_OIII_5006']))[i])