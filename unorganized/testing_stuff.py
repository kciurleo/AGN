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


df=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv', dtype=str)

names = ['2CXO J134736.4+173404','2CXO J131651.2+055647','2CXO J235720.1-005829','2CXO J104429.3+113810']

new_df = pd.DataFrame(columns=df.columns)

for name in names:
    row = df.loc[df['CSC21P_name'] == name].head(1)
    new_df = pd.concat([new_df, row],ignore_index=True)

additionalrow = df.loc[(df['CSC21P_name'] == '2CXO J135317.9+332929') & (df['CHANDRA_OBSID'] == '4867')]

new_df = pd.concat([new_df, additionalrow], ignore_index=True)
new_df.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/katie_testcoords.csv', index=False)


print(np.min(df['Flux_OIII_5006']))

nonzero = df.loc[df['Flux_OIII_5006'] != '0.0' ]
print(len(df['Flux_OIII_5006']))
print(len(nonzero['Flux_OIII_5006']))
for i in range(len(set(nonzero['Flux_OIII_5006']))):
    print(list(set(nonzero['Flux_OIII_5006']))[i])
'''
data = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CSC2.1p_OIR_SDSSspecmatch.csv')
names = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/CorrectedNamesCSC21.txt', skiprows=1, names=['current name', 'corrected name'])

seyferts = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/seyferts.csv')

seth_candidates = pd.read_csv('/Users/kciurleo/Documents/kciurleo/all_info_final.csv')
set1 = set([1,2,2,3,4])
set2 = set([5,6,6,6,0])

weird_names_in_seyferts = list(set(names['current name']).intersection(set(seyferts['CSC21P_name'])))
print(len(weird_names_in_seyferts))
weird_names_in_seth = list(set(names['corrected name']).intersection(set(seth_candidates['# Name'])))
print(len(weird_names_in_seth))
weird_data = list(set(names['corrected name']).intersection(set(data['CSC21P_name'])))
print(len(weird_data))

anybody = pd.DataFrame(columns=seyferts.columns)
for i in np.array(names['corrected name']):
    row = seyferts.loc[seyferts['CSC21P_name']==i]
    anybody._append(row)

print(anybody)