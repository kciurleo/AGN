import numpy as np
import pandas as pd
import os
from astropy.io import fits
import glob
from ciao_contrib.runtool import *
from matplotlib import pyplot as plt

#Read all the match errors in, along with all the info about them
match_error = pd.read_csv('/opt/pwdata/katie/csc2.1/matching_error.txt', skiprows=1, names=['ids', 'date', 'exp', 'theta'])
final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
match_error_full_info = pd.DataFrame(columns=final_list.columns)

#Empty columns
dates = []
exps = []
thetas = []
radii = []
problem_list = []

#Get the exposure time, date, and off-axis angle for all the matching errors
print('Getting fits info and off axis angle')
for number, row in match_error.iterrows():
    #exp time and date from header
    try:
        file = glob.glob(f'/opt/pwdata/katie/csc2.1/{row["ids"]}/primary/*evt2*')[0]
    except:
        dates.append(np.nan)
        exps.append(np.nan)
        thetas.append(np.nan)
        problem_list.append(row['ids'])
        continue

    #print(f'Getting fits info for {row["ids"]}')
    hdr = fits.getheader(file,ext=1)
    dates.append(hdr['DATE-OBS'])
    exps.append(hdr['EXPOSURE'])

    #off axis angle from ciao tool
    #print(f'Getting off axis angle for {row["ids"]}')
    temprow=final_list.loc[final_list['OBSID']==f'{row["ids"]}']
    dmcoords.punlearn()
    dmcoords(file, option='cel', ra=list(temprow['RA'])[0], dec=list(temprow['DEC'])[0])
    thetas.append(dmcoords.theta)

    #radius based on off axis angle
    if dmcoords.theta <= 1:
        radius = 1
    else:
        radius = dmcoords.theta
    radii.append(radius)

#Fill all the columns
match_error['date'] = dates
match_error['exp'] = exps
match_error['theta'] = thetas
match_error['radius'] = radii

print(f'Finished off-axis angles and getting full info.')
print(f'Error finding evt2 file for the following ids: {problem_list}')

#Combine the full info with the match errors
print('Getting full info.')
for obsid in match_error['ids']:
    #print(f'Getting full info for {obsid}')
    temp_row_dude=final_list.loc[final_list['OBSID']==f'{obsid}']
    match_error_full_info = pd.concat([match_error_full_info, temp_row_dude], ignore_index=True)

match_error_full_info = pd.merge(match_error_full_info, match_error, left_on="OBSID", right_on="ids", how="left")

#Run srcflux on all the match errors
print('Running srcflux')
for number, row in match_error_full_info.iterrows():
    try:
        file = glob.glob(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/*evt2*')[0]
    except:
        continue
    
    os.chdir(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary')
    
    print('writing reg files for ',row["OBSID"])
    
    srcfile = 'testsrc.reg'
    bkgfile = 'testbkg.reg'

    with open(srcfile, 'w') as regfile:
        regfile.write(f'circle({row["RA"]}d,{row["DEC"]}d,{row["radius"]}\")')

    with open(bkgfile, 'w') as regfile2:
        regfile2.write(f'annulus({row["RA"]}d,{row["DEC"]}d,{row["radius"]}\",{1.5*row["radius"]}\")')

    print('srcfluxing ',row["OBSID"])
    srcflux.punlearn()
    srcflux(f'{file}[energy=300:7500]', pos=f'{row["RA"]}, {row["DEC"]}', srcreg=srcfile, bkgreg=bkgfile, outroot=f"/opt/pwdata/katie/csc2.1/{row['OBSID']}/primary/counts/", psfmethod="quick", clobber="yes") 

    counts = []

#Get the counts from the correct files
for number, row in match_error_full_info.iterrows():
    try:
        file = glob.glob(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/*evt2*')[0]
    except:
        continue
    
    os.chdir(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary')
    
    print('looking at ', row["OBSID"])
    try:
        count = fits.getdata(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/counts/broad.flux')['COUNTS'][0]
    except:
        try:
            #some of the files get named with the _ in front and some don't. idk why.
            count = fits.getdata(f'/opt/pwdata/katie/csc2.1/{row["OBSID"]}/primary/counts/_broad.flux')['COUNTS'][0]
        except:
            count = np.nan
    
    print(row["OBSID"],' has ',count,' counts')
    counts.append(count)

match_error_full_info['counts']=counts

#Save file
match_error_full_info.to_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/match_error_srcflux.csv', index=False)

plt.figure(figsize=(8,6))
plt.hist(match_error_full_info['counts'], bins=30)
plt.title('Matching Errors - Individual Source Detection')
plt.xlabel('Counts')
plt.savefig("/Users/kciurleo/Documents/kciurleo/AGN/plots/matching_error.pdf", format="pdf")