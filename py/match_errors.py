import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from ciao_contrib.region.check_fov import FOVFiles
import glob

seyferts = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/full_process_input.csv')[['CSC21P_name', 'CHANDRA_OBSID', ' OBSDATE', ' TIME', 'MJD','PLATE','FIBERID']]
match_errors = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_error_srcflux.csv')
final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',engine='python',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])

'''
nums=[]
presents=[]
for i, row in match_errors.iterrows():
    #Get the total number of obsids for a given name
    subdude=seyferts.loc[seyferts['CSC21P_name']==row['NAME']]
    num = len(subdude['CHANDRA_OBSID'].unique())
    nums.append(num)

    #Get whether or not the thing is in the fov file
    try:
        file = glob.glob(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/*fov1.fits*')[0]
    except:
        presents.append(np.nan)

    my_obs=FOVFiles(file)
    ii=my_obs.inside(row["RA"], row["DEC"])
    if len(ii)==0:
        presents.append(False)
    else:
        presents.append(True)
    print(f'finished {row["NAME"]}')


match_errors['NUM']=nums
match_errors['PRESENT']=presents

#match_errors.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_error_srcflux.csv', index=False)

print(match_errors)

'''
present = match_errors.loc[match_errors['PRESENT']==True]
not_present = match_errors.loc[match_errors['PRESENT']==False]
present_unique=present.drop_duplicates(subset=['NAME'])

present_only_one=present_unique.loc[present_unique['NUM']==1]
present_multiple=present_unique.loc[present_unique['NUM']>1]

#check to make sure all the guys who have multiple have at least one obs where they went through
yes_list=[]

for i, row in present_multiple.iterrows():
    subdude=final_list.loc[final_list['NAME']==row['NAME']]
    for i2, row2 in subdude.iterrows():
        if row2['COUNTS']!='NO MATCH':
            yes_list.append(row['NAME'])
            break

safe_present_multiple = present_multiple[present_multiple['NAME'].isin(yes_list)]

bad_present_multiple = present_multiple[~present_multiple['NAME'].isin(yes_list)]

all_naughty_guys = bad_present_multiple.merge(present_only_one, how='outer')

print(f"{len(present['NAME'])} of {len(match_errors['NAME'])} obsid-object combos are present on the chips.")
print(f"{len(not_present['NAME'])} of {len(match_errors['NAME'])} obsid-object combos are on chip gaps (outside the FOV file)")
print()
print(f'Of those obsid-object combos present in their observations, there are {len(present_unique["NAME"])} unique objects.')
print(f'Out of these unique objects, {len(present_only_one["NAME"])} are the only observation of their object and {len(present_multiple["NAME"])} objects have other observations.')
print()
print(f'Of those with multiple observations, {len(safe_present_multiple["NAME"])} have at least one observation which was matched.')
print(f'{len(bad_present_multiple["NAME"])} had match errors for all their multiple observations.')
print()
print(f'There are therefore {len(all_naughty_guys["NAME"])} objects which are present on their chips but are unmatched in all their observations (either one or multiple).')

plt.figure(figsize=(8,6))
plt.hist(all_naughty_guys['counts'], bins=40)
plt.title('Matching Errors - Present Fully Unmatched Objects')
plt.xlabel('Counts')
plt.show()

