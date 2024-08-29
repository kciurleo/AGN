#File edited 7/3/2024 by Katie Ciurleo from Seth Larner 3/9/2024, edits marked in comments and Seth's work preserved in comments or '''

print('Importing...')
import time
import numpy as np
import sys
import glob
import os
from os import path
import pandas as pd
from ciao_contrib.runtool import *
from PyAstronomy import pyasl #used for unit conversion
from bxa.sherpa.background.models import ChandraBackground
from bxa.sherpa.background.fitters import SingleFitter
from get_abs_sherpa_bxa import *
from collate_for_fp import *
import smtplib, ssl
from compton_check_no_chaser import get_OIII, get_ratio
from calc_cosmos_for_fp import cosmo_calc
from get_abs_sherpa_bxa_alt import get_abs_alt
from get_abs_sherpa_bxa_restricted import get_abs_restricted
from make_stat_table import *
from best_model import *

xspec_init_command = 'hea'
xspec_start_command = 'xspec'
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']


'''
ATTN: Before running search for "uncomment" incase I forgot to uncomment required commented-out lines

    This script fully processes x-ray data of AGNs and fits a dually absorbed powerlaw.

    It is written to run in the (admitably niche) case where sources are known
    but have not yet matched to x-ray observation so no regions have been created and no spectra have been extracted

    It assumes you have used chaser or download_chandra_obsid to download observations
    which may contain your sources and that you have the  prequsite text files of information described below

    The needed inputs are as follows:
        data_dir
            Example: '../x-ray/quar'
            data_dir is the directory where the script looks for obsid data
            It assumes evt2 files are in data_dir/obsid/primary/
            If they've been reprocessed, find and replace primary with repro
        outroot
            Example: '../x-ray/quar/full_process_test'
            outroot will be used to name outgoing files
            Please include directory
            Tested with outroot being in data_dir
        coords_path
            Example: '../x-ray/quar/coords.txt'
            coords_path is the path to your coordinate text file
            Coordinates text file should be a plain text file containing source name, ra, dec, z, these information are required
            The script assumes the delimiter is two spaces ('  ')
            Change delim as needed
        chaser_path
            Example: '../x-ray/quar/chaser.csv'
            chaser_path is the path to the chaser csv file
            The chaser csv file is the csv of chaser information downloaded from chaser, must use decimal degrees
            May need to be lightly edited if loadtxt throws error
                Sometimes doesn't like the last column in the csv
            Edited 7/3/2024: if 'no', assume no chaser_path and use the previous matching method
        Edited 7/3/2024:
        nH_clobber
            'yes' or 'no'
            Same as wav_clobber but for nH
            No recommendation from Seth
        End edit
        wav_clobber
            'yes' or 'no'
            If yes, wavdetect will be run on all sources
            If no, wavdetect will only be run on those source which do not have data products from wavdetect
            Reccomended to run with wav_clobber = 'no'
        spec_clobber
            'yes' or 'no'
            Same as wav_clobber but for specextract
            I am hesitant to reccomend, because the copying step may overwrite the desired source spectra for all observations b, c, d etc.
        Edited 7/3/2024:
        bkg_clobber
            'yes' or 'no'
            Same as wav_clobber but for background
            No recommendation from Seth
        End edit

    The script is run by envoking "python [script path] [data_dir] [outroot] [coords_path] [chaser_path] [nh_clobber] [wav_clobber] [spec_clobber] [bkg_clobber]"
    The shell running the script must be configured to run the nH ftool and ciao

    The script runs through the following steps:
        1) Match x-ray observations to sources
        2) Find galactic nH values of sources
        3) Run  fluximage and wavdetect
        4) Match wavdetect created regions to sources
        5) Make background regions
        6) Run specextract on the created regions
        7) Make prep files to be read by tcl script
        8) Create source summary document
        9) Instruct user to run tcl script
        10) Read tcl logs and identify minimally absorbed sources
        11) Summarizes fit information of minimally absorbed sources

    In the middle, the script will pause and wait for the user to run get_abs.tcl
    Edited 7/3/2024: no it doesn't.

    The part before the pause is much longer than after.
    Wavdetect and specextract and particularly long time sinks

Enjoy!
'''


#############
#Defining functions
def match_test(test_ra,test_dec,match_ra,match_dec,thresh):#takes in coordinates and does a radial search to determine their match up to the given threshold
    #where test are the coordinates to be tested and match are the coordinates being tested against

    #add high/low RA exception
    if test_ra > 359:
        test_ra -= 360
    if match_ra > 359:
        match_ra -= 360
    distance = ((test_ra - match_ra)**2 + (test_dec - match_dec)**2)**(1/2)
    if distance <= thresh:
        return True
    else:
        return False

def unglob(list): #unglob reformats files matched with the glob command
    list = list[0]
    list = str(list)
    list = list.strip('[]')
    list = list.strip("''")
    return list

def detect(dir): #detect is used to run fluximage and wavdetect in sequence on an obsid
    #needs a level 2 directory with a chandra evt2 file
    fluximage.punlearn()
    evt = glob.glob(f'{dir}/*evt2*')
    evt = unglob(evt)
    fluximage.infile=evt
    fluximage.outroot = f'{dir}/detect'
    fluximage.bands = '0.3:7.5:2.3'
    fluximage.psfecf=0.9 #one sigma of 2D gaussian (see 'running wavdetect')
    fluximage.clobber = 'yes'
    fluximage()

    wavdetect.punlearn()
    img = glob.glob(f'{dir}/*thresh.img')
    img = unglob(img)
    wavdetect.infile = img
    psf = glob.glob(f'{dir}/*thresh.psfmap')
    psf = unglob(psf)
    wavdetect.psffile = psf
    wavdetect.outfile = f'{dir}/detect_src.fits'
    wavdetect.imagefile = f'{dir}/detect_imgfile.fits'
    wavdetect.regfile = f'{dir}/detect_src.reg'
    wavdetect.defnbkgfile = f'{dir}/detect_nbgd.fits'
    wavdetect.scellfile = f'{dir}/detect_scell.fits'
    wavdetect.clobber = 'yes'
    wavdetect()

def countcheck(evt,reg): #when given a evt file and a region, returns the number of counts between .3 and 7.5 KeV
    dmlist.punlearn()
    dmlist.infile = f'{evt}[sky=region({reg}),energy=300:7500]'
    dmlist.opt = 'counts'
    return int(dmlist())

def make_bkg(src_reg,all_reg,size): #makes a background annulus with outer radius controlled by 'size'
    outfile = src_reg[:-7]
    outfile = outfile + 'bkg.reg'
    region = np.loadtxt(src_reg,dtype='str')
    region = str(region)
    region = region[8:-1]
    all_region = str(np.loadtxt(all_reg,dtype='str',skiprows=3)).rstrip('#').strip('[]').strip("''")#skip rows added to adjust to ds9 formatting, as in reg_match.py
    all_region = all_region.split('\n')
    region_list = region.split(",")
    region_axis_1 = float(region_list[2][:-1])
    region_axis_2 = float(region_list[3][:-1]) #have to convert the axis values from sec to min
    region_axis_1 *= 0.01667 #converts to arcminutes
    region_axis_2 *= 0.01667
    if region_axis_1 > region_axis_2:
        bkg_radius = region_axis_1
    else:
        bkg_radius = region_axis_2
    out = open(outfile,'w')
    bkg_reg = f"annulus({region_list[0]},{region_list[1]},{bkg_radius*1.5}',{(bkg_radius*1.5)+size}')"
    out.write(bkg_reg)
    out.close()
    out = open(outfile,'a')
    for line in all_region:
        line = line.strip()
        line = line.strip("''")
        out.write(f'\n -{line}')
    out.close()

def find_bkg(dir, limit): #when given an appropriate level 2 directory runs make_bkg until it finds a background with at least {limit} on-energy counts
    stop = False
    evt = glob.glob(f'{dir}/*evt2*')
    evt = unglob(evt)
    src_reg = dir + '/src.reg'
    all_reg = dir + '/detect_src_sky.reg'
    i = 0

    while not stop:
        try:
            make_bkg(src_reg,all_reg,np.arange(.001667,1.5,.001667)[i])#radius goes from 0 to 1.5 arcminute in .1 arcsec steps
            i +=1 #if the  regions seem bigger than they should be, its a problem with using arcminutes, use arcseconds instead
            bkg = dir + '/bkg.reg'
            check = countcheck(evt,bkg)
            if check > limit:
                stop = True
        except IndexError:
            stop = True
            print(f'1.5 arcmin limit reached, bkg has {countcheck(evt,bkg)} counts')

def make_spec(dir): #needs a directory which contains a level 2 event file, a source region, and a background region
    specextract.punlearn()
    evt = unglob(glob.glob(f'{dir}/*evt2*'))
    bkgreg = f'{dir}/bkg.reg'
    reg = f'{dir}/src.reg'
    file = f'{evt}[sky=region({reg})]'
    bkgfile = f'{evt}[sky=region({bkgreg})]'
    specextract.infile = file
    specextract.bkgfile = bkgfile
    specextract.outroot = f'{dir}/reextract_pha'
    specextract.weight = 'no'
    specextract.correctpsf = 'yes'
    specextract.clobber = 'yes'
    #specextract.energy = '0.3:7.5:0.01'
    specextract()

#Done in collate_for_fp.py
'''
def move_to_min_abs(obsid,min_abs_dir,data_dir): #copies files for the indicated obsid to the min abs directory
    newdir = f'{min_abs_dir}/{obsid}'
    try:
        os.system(f'mkdir {newdir}')
    except:
        pass
    new_file = f'{min_abs_dir}/{obsid}/abs_summary.txt'
    os.system(f'cp {data_dir}/{obsid}/primary/sherpaout.txt {new_file}')
    os.system(f'cp {data_dir}/{obsid}/primary/contour_in.ps {min_abs_dir}/{obsid}/contour_in.ps')
    os.system(f'cp {data_dir}/{obsid}/primary/ldata_fit.ps {min_abs_dir}/{obsid}/ldata_fit.ps')
    os.system(f'cp {data_dir}/{obsid}/primary/ldata_fit_ungroup.ps {min_abs_dir}/{obsid}/ldata_fit_ungroup.ps')
    os.system(f'cp {data_dir}/{obsid}/primary/find_abs.log {min_abs_dir}/{obsid}/find_abs.log')
'''


def main():

    cwd = os.getcwd()

    ############
    #Start with reading in the inputs from the user
    print('Reading in...')
    if len(sys.argv) != 10:
        print('Inputs not recognized')
        print('Try:')
        print(f'python {sys.argv[0]} [data_dir] [outroot] [coords_path] [chaser_path] [nh_clobber] [wav_clobber] [spec_clobber] [bkg_clobber] [fit_clobber]')
        raise Exception

    data_dir = sys.argv[1]
    outroot = sys.argv[2]
    outroot_text = outroot.split('/')[-1]
    coords_path = sys.argv[3]
    chaser_path = sys.argv[4]
    nh_clobber = sys.argv[5]
    wav_clobber = sys.argv[6]
    spec_clobber = sys.argv[7]
    bkg_clobber=sys.argv[8]
    fit_clobber = sys.argv[9]

    #check and make sure inputs are valid
    if 'n' in wav_clobber:
        wav_clobber = 'no'
    elif 'y' in wav_clobber:
        wav_clobber = 'yes'
    else:
        sys.exit('Wavdetect clobber not recognized')

    if 'n' in spec_clobber:
        spec_clobber = 'no'
    elif 'y' in spec_clobber:
        spec_clobber = 'yes'
    else:
        sys.exit('Specextract clobber not recognized')

    if 'n' in bkg_clobber:
        bkg_clobber = 'no'
    elif 'y' in bkg_clobber:
        bkg_clobber = 'yes'
    else:
        sys.exit('Background clobber not recognized')

    if 'n' in fit_clobber:
        fit_clobber = 'no'
    elif 'y' in fit_clobber:
        fit_clobber = 'yes'
    else:
        sys.exit('Fit clobber not recognized')

    if 'n' in nh_clobber:
        nh_clobber = 'no'
    #Edit 7/3/2024
    #elif 'y' in fit_clobber:
    elif 'y' in nh_clobber:
    #End edit
        nh_clobber = 'yes'
    else:
        sys.exit('nH clobber not recognized')

    if not path.exists(data_dir):
        sys.exit(f'Data directory {data_dir} does not exist')

    #Edit 7/3/2024
    try:
        chaser_data = np.loadtxt(chaser_path,delimiter=',',dtype='str')
    except:
        print('No chaser data found. Matching on coordinates.')
    #end edit

    coords_data = np.loadtxt(coords_path,delimiter=',', dtype='str', comments=None) #may need to be changed
    coords_df = pd.read_csv(coords_path)

    if spec_clobber == 'no':
        print('***Warning: not clobbering spectrum may lead to overwrite issues***')
        time.sleep(3)

    ##############
    #Then we match the observations to the sources which may be contained therein
    #Matching an obsid does not guarantee the source was actually observed
    
    print('Matching observations...')
    matched_obsids = []
    matched_name = []
    matched_ra = []
    matched_dec = []
    matched_z = []

    #Edited 7/3/2024
    if chaser_path == 'no':
        coords_header = coords_data[0,::]
        #change these as needed to adapt to your csv
        name_header = 'CSC21P_name'
        obsid_header = 'CHANDRA_OBSID'
        ra_header = 'ra_x'
        dec_header = 'dec_x'
        z_header = 'Z'
        for i, header in enumerate(coords_header):
            if header == name_header:
                matched_name = coords_data[1:,i]
            elif header == obsid_header:
                matched_obsids = coords_data[1:,i]
            elif header == ra_header:
                matched_ra = coords_data[1:,i]
            elif header == dec_header:
                matched_dec = coords_data[1:,i]
            elif header == z_header:
                matched_z = coords_data[1:,i]
    #All code in "else" was present prior to edit
    else:
        chaser_RA  = chaser_data[1:,8]
        chaser_dec = chaser_data[1:,9]
        obsids = chaser_data[1:,1]
        source_RA = coords_data[::,1]
        source_dec = coords_data[::,2]
        source_z = coords_data[::,3]
        source_names = coords_data[::,0]

        #Edited 7/3/2024
        #with open(f'{outroot}_obsid_matching_error.txt', 'w') as match_error:
        with open(f'{outroot}/obsid_matching_error.txt', 'w') as match_error:
        #End edit
            match_error.write('#The following sources did not get matched to an observation')
            for j in range(len(source_RA)):
                match = 0
                for i in range(len(chaser_RA)):
                    try:
                        if match_test(float(chaser_RA[i]),float(chaser_dec[i]),float(source_RA[j]),float(source_dec[j]),.5):
                            matched_obsids.append(obsids[i])
                            matched_name.append(source_names[j])
                            matched_ra.append(source_RA[j])
                            matched_dec.append(source_dec[j])
                            matched_z.append(source_z[j])
                            match += 1
                            #We don't break here because a single source on the source list can match to multiple observation
                    except ValueError as e:
                        print(chaser_RA[i])
                        print(chaser_dec[i])
                        raise e
                if match == 0:
                    print(f'{source_names[j]} not matched to observation')
                    match_error.write('\n'+source_names[j])

        #Edited 7/3/2024
        #with open(f'{outroot}_need_to_download.txt','w') as download_doc:
        with open(f'{outroot}/need_to_download.txt','w') as download_doc:
        #End edit
            download_doc.write('#This document records the observations which need to be downloaded')
            for i, obsid in enumerate(matched_obsids):
                obsid_dir = f'{data_dir}/{obsid}'
                if not path.exists(obsid_dir):
                    download_doc.write('\n' + obsid)
                    del matched_obsids[i]
                    del matched_name[i]
                    del matched_ra[i]
                    del matched_dec[i]
                    del matched_z[i]
    #End edit

    data_out_obsidmatch = np.column_stack((matched_name,matched_obsids,matched_ra,matched_dec,matched_z))
    print('matched succesfully')


    ##############
    #next we need the nH values
    #must being running code in shell configured with the nH ftool
    print('Calculating galactic nH...')
    RAs = data_out_obsidmatch[::,2]
    decs = data_out_obsidmatch[::,3]

    #Edit 7/3/2024
    #if not nh_clobber:
    if nh_clobber == 'yes' or not path.exists(f'{cwd}/nh.log'):
        try:
            os.system(f'rm {cwd}/nh.log')
        except:
            pass
        #added cwd, since nh spits out the log on cwd
    #End edit

        for i in range(len(RAs)):
            out = f'nh equinox=2000, ra={RAs[i]}, dec={decs[i]}, tchat=0, lchat=5'
            os.system(out)
    #Edited 7/3/2024
    #nh = open('nh.log','r').read().split('\n')
    nh = open(f'{cwd}/nh.log','r').read().split('\n')
    #End edit
    nh_out= []
    for line in nh:
        if 'Weighted average nH (cm**-2)' in line:
            nh_out.append(line[-8:])
    nh_out = np.asarray(nh_out,dtype='float64')
    nh_out /= 1E22
    nh_out = np.asarray(nh_out,dtype='str')
    data_out_nh = np.column_stack((data_out_obsidmatch,nh_out))
    print('found nH succesfully')


    ##############
    #Next up, we need to run wavdetect on the obsids
    #We first run fluximage so that we can apply a psf correction
    print('Running fluximage and wavdetect...')
    #Edited 7/3/2024
    #with open(outroot + '_wavdetect_error.txt', 'w') as error_doc:
    with open(outroot + '/wavdetect_error.txt', 'w') as error_doc:
    #End edit
        error_doc.write('#This doc records the sources which fail during wavdetect or fluximage')
        obsids_u = np.unique(data_out_nh[::,1]) #obsids list has not yet been made unique and we only need to run
        for i,obsid in enumerate(obsids_u):       #wavdetect once per events file, even if it appears twice in our list
            print(f'Running wavdetect on {obsid}, {i+1} of {len(obsids_u)}')
            dir = f'{data_dir}/{obsid}/primary'
            if wav_clobber == 'yes' or not path.exists(f'{data_dir}/{obsid}/primary/detect_src.reg'):
                try:
                    detect(dir)
                except:
                    print('wavdetect failed')
                    error_doc.write(f'{obsid} failed during wavdetect or fluximage\n')
            else:
                print('Wavdetect already run and clobber is no')


    ##############
    #Now we need to make the obsids unique
    #This code works on the assumption that there is only one source per obsid but this might not be the case
    #This fixes that by naming the second source in a given obsid '{obsid}b', the third '{obsid}c', etc.
    #And then copying over the directory under the new name
    print('Checking unquiness...')
    uniques = []
    for i, obsid in enumerate(data_out_nh[::,1]):
        repeat = True
        while repeat:

            if obsid not in uniques:
                uniques.append(obsid)
                repeat = False
                data_out_nh[i,1] = obsid

                #if we need to copy the
                if obsid[-1] in alphabet and not path.exists(f'{data_dir}/{obsid}'):
                    print(f'Copying to {obsid}')
                    cp_command = f'cp -R {data_dir}/{obsid[:-1]} {data_dir}/{obsid}'
                    os.system(cp_command)

            else:
                if obsid[-1] in alphabet:
                    obsid = obsid[:-1] + alphabet[alphabet.index(obsid[-1])+1]
                else:
                    obsid = obsid + 'b'


    ##############
    #next up, we match the sources to the regions we just created to make the source regions
    print('Matching to regions...')
    no_matches = []
    yes_matches = []
    #Edited 7/3/2024
    #with open(f'{outroot}_matching_error.txt','w') as no_matches_doc:
    with open(f'{outroot}/matching_error.txt','w') as no_matches_doc:
    #End edit
        no_matches_doc.write('#This doc records which sources did not get matched to a region')
        obsids = data_out_nh[::,1]

        #Edited 7/3/2024
        #with open(outroot + '_wavdetect_error.txt', 'r') as check_error_doc:
        with open(outroot + '/wavdetect_error.txt', 'r') as check_error_doc:
        #End edit
            check_error = check_error_doc.read()

            for i,ob in enumerate(obsids):
                print(f'Testing {ob}, {i+1} of {len(obsids)}')

                if ob in check_error:
                    print(f'wavdetect failed for {ob}, skipping it')
                    continue
                elif ob[-1] in alphabet and ob[:-1] in check_error:
                    print(f'wavdetect failed for {ob}, skipping it')
                    continue

                all_region_sky = f'{data_dir}/{ob}/primary/detect_src_sky.reg'
                all_region_phys = f'{data_dir}/{ob}/primary/detect_src.reg'
                evt = unglob(glob.glob(f'{data_dir}/{ob}/primary/*evt2*'))
                regphystocel.punlearn()
                regphystocel.infile = all_region_phys
                regphystocel.outfile = all_region_sky
                regphystocel.wcsfile = evt
                regphystocel.clobber = 'yes'
                try:
                    regphystocel()
                except OSError:
                    no_matches_doc.write(f'\n{ob}')
                    continue

                regiontxt = np.loadtxt(all_region_sky,dtype='str',skiprows=3)
                match = 0
                try:
                    for line in regiontxt: #this breaks when there is only one source detected, fixed by the except
                        coords = line[7:].strip('()')#removes 'ellipse' marker and parenthases
                        coords_list = coords.split(',')
                        ra = coords_list[0]
                        dec = coords_list[1]
                        radius1 = float(coords_list[2].strip('"'))
                        radius2 = float(coords_list[3].strip('"'))
                        radius = (radius1,radius2)
                        radius = max(radius)#radius is in arcseconds
                        radius *= 2.778E-4
                        if dec[0] != '-':
                            pm = '+'
                        else:
                            pm = ''
                        coord_str = f'{ra} {pm}{dec}' #formats the string to be passed to pyasl
                        ra,dec = pyasl.coordsSexaToDeg(coord_str)
                        #now we are ready to test
                        if match_test(float(RAs[i]),float(decs[i]),ra,dec,radius):
                            match += 1
                            out = open(f'{data_dir}/{ob}/primary/src.reg', 'w')
                            out.write(line)
                            out.close()
                            #when the match is found we want to use this line to create the src.reg file for later programs
                except TypeError:
                    if regiontxt is not None:
                        line = str(regiontxt)
                        coords = line[7:].strip('()')#removes 'ellipse' marker and parenthases
                        coords_list = coords.split(',')
                        ra = coords_list[0]
                        dec = coords_list[1]
                        radius1 = float(coords_list[2].strip('"'))
                        radius2 = float(coords_list[3].strip('"'))
                        radius = (radius1,radius2)
                        radius = max(radius)#radius is in arcseconds
                        radius *= 2.778E-4
                        if dec[0] != '-':
                            pm = '+'
                        else:
                            pm = ''
                        coord_str = f'{ra} {pm}{dec}' #formats the string to be passed to pyasl
                        ra,dec = pyasl.coordsSexaToDeg(coord_str)
                        #now we are ready to test
                        if match_test(float(RAs[i]),float(decs[i]),ra,dec,radius):
                            match += 1
                            out = open(f'{data_dir}/{ob}/primary/src.reg', 'w')
                            out.write(line)
                            out.close()
                    else:
                        print('Something is wrong') #shitty error handling
                        continue
                if match == 0:
                    no_matches.append(ob)
                    no_matches_doc.write('\n'+ob)
                elif match == 1:
                    yes_matches.append(ob)
                else:
                    print('bad') #the best error handling
                    #this trips if a source matches to two (or more) regions
                    #they would have to be overlapping
                    #Even if it happens, it isn't the biggest deal
                i +=1


    ############
    #Next we make the background regions
    print('Making background regions...')
    limit = 50 #sets the number of counts to put in a background region

    j = 1
    for obsid in yes_matches:
        if obsid == '': #weird error handling, nothing to see here
            continue
        print(f'Making background region for {obsid}, {j} of {len(yes_matches)}')
        j += 1
        if bkg_clobber == 'yes' or not path.exists(f'{data_dir}/{obsid}/primary/bkg.reg'):
            find_bkg(f'{data_dir}/{obsid}/primary', limit)


    ############
    #Now we specextract
    print('Extracting spectrum...')
    #Edited 7/3/2024
    #with open(f'{outroot}_spec_error.txt','w') as spec_error_doc:
    with open(f'{outroot}/spec_error.txt','w') as spec_error_doc:
    #End edit
        spec_error_doc.write('#This doc records the sources which fail during specextract\n')

        for i, obsid in enumerate(obsids):
            #Edited 7/3/2024
            #check_error = open(outroot + '_wavdetect_error.txt', 'r').read()
            check_error = open(outroot + '/wavdetect_error.txt', 'r').read()
            #End edit
            print(f'Running specextract on {obsid}, {i+1} of {len(obsids)}')

            if obsid in check_error:
                print(f'wavdetect failed for {obsid}, skipping it')
                continue
            elif obsid[-1] in alphabet and obsid[:-1] in check_error:
                print(f'wavdetect failed for {obsid}, skipping it')
                continue

            if obsid in no_matches:
                print(f'Region finding failed for {obsid}, skipping it')
                continue

            if spec_clobber == 'yes' or not path.exists(f'{data_dir}/{obsid}/primary/reextract_pha.pi'):
                try:
                    make_spec(f'{data_dir}/{obsid}/primary')
                except OSError: #specextract runs into problems if src.reg is 0 counts
                    spec_error_doc.write(dir+'\n')
            else:
                print('specextract already run and clobber is no')


    '''
    Code depreciated
    ############
    #Next we need to invoke and run fitbkg.py for each of the obsids
    #Requires bkg and data files as inputs
    print('Running fitbkg.py...')
    for i, obsid in enumerate(data_out_nh[::,1]):
        #have to check for errors here that would prevent a spectrum from being made which in turn prevents fitbkg from running
        data_file = f'{data_dir}/{obsid}/primary/reextract_pha.pi'
        bkg_file = f'{data_dir}/{obsid}/primary/reextract_pha_bkg.pi'
        if path.exists(bkg_file) and path.exists(data_file):
            os.system(f'python ./BXA-master/autobackgroundmodel/fitbkg.py "{bkg_file}" "{data_file}"')
        else:
            print(f'Skipping running for {obsid}, check error logs for details')
    '''


    #############
    #Next we prep the necessary files for running the tcl script
    print('Prepping for fitting...')
    os.chdir(cwd)
    #make the counts array here so we can filter tcl inputs for count threshold
    counts = []

    for obsid in data_out_nh[::,1]:
        src_reg = f'{data_dir}/{obsid}/primary/src.reg'
        if path.exists(src_reg):
            evt = unglob(glob.glob(f'{data_dir}/{obsid}/primary/*evt2*'))
            counts.append(str(countcheck(evt,src_reg)))
        else:
            counts.append('NO MATCH')

    out_full = np.column_stack((data_out_nh,counts))
    #Edited 7/3/2024
    #error_check = open(f'{outroot}_spec_error.txt','r').read()
    error_check = open(f'{outroot}/spec_error.txt','r').read()
    #End edit

    o_out = []
    z_out = []
    n_out = []
    o_out_lowcount = []
    z_out_lowcount = []
    n_out_lowcount = []

    for i, obsid in enumerate(out_full[::,1]):
        if obsid in yes_matches and obsid not in error_check and int(counts[i]) >= 40: #a source must have succesfully matched and have its spectrum extracted
            o_out.append(obsid)
            z = data_out_nh[i,4]
            z_out.append(z)
            n = data_out_nh[i,5]
            n_out.append(n)
        elif obsid in yes_matches and obsid not in error_check and int(counts[i]) < 40:
            o_out_lowcount.append(obsid)
            z = data_out_nh[i,4]
            z_out_lowcount.append(z)
            n = data_out_nh[i,5]
            n_out_lowcount.append(n)
    #Edited 7/3/2024
    '''
    o_out_file = open(f"{outroot}_tcl_obsids.txt", 'w')
    z_out_file = open(f"{outroot}_tcl_zs.txt", 'w')
    n_out_file = open(f"{outroot}_tcl_nhs.txt", 'w')
    '''
    o_out_file = open(f"{outroot}/tcl_obsids.txt", 'w')
    z_out_file = open(f"{outroot}/tcl_zs.txt", 'w')
    n_out_file = open(f"{outroot}/tcl_nhs.txt", 'w')
    #End edit

    for o, z, n in zip(o_out,z_out,n_out):
        o_out_file.write(o + '\n')
        z_out_file.write(z + '\n')
        n_out_file.write(n + '\n')
    o_out_file.close()
    z_out_file.close()
    n_out_file.close()

    #Edited 7/3/2024
    '''
    o_out_file_lowcount = open(f"{outroot}_tcl_obsids_lowcount.txt", 'w')
    z_out_file_lowcount = open(f"{outroot}_tcl_zs_lowcount.txt", 'w')
    n_out_file_lowcount = open(f"{outroot}_tcl_nhs_lowcount.txt", 'w')
    '''
    o_out_file_lowcount = open(f"{outroot}/tcl_obsids_lowcount.txt", 'w')
    z_out_file_lowcount = open(f"{outroot}/tcl_zs_lowcount.txt", 'w')
    n_out_file_lowcount = open(f"{outroot}/tcl_nhs_lowcount.txt", 'w')
    #End edit

    for o, z, n in zip(o_out_lowcount,z_out_lowcount,n_out_lowcount):
        o_out_file_lowcount.write(o + '\n')
        z_out_file_lowcount.write(z + '\n')
        n_out_file_lowcount.write(n + '\n')
    o_out_file_lowcount.close()
    z_out_file_lowcount.close()
    n_out_file_lowcount.close()


    ##############
    #Call the fitting function to fit
    print('Fitting...')
    i = 0
    #Edited 7/3/2024
    #with open(f'{outroot}_fitting_error.txt','w') as error_doc:
    with open(f'{outroot}/fitting_error.txt','w') as error_doc:
    #End edit
        error_doc.write('#Records obsids which errored during fitting.')
        for o, z, n in zip(o_out,z_out,n_out):
            print(f'Fitting {o}, {i+1} of {len(o_out)}')
            dir = f'{data_dir}/{o}/primary'
            already_fit = path.exists(f'{dir}/sherpaout.txt') and path.exists(f'{dir}/sherpaout_alt.txt') and path.exists(f'{dir}/sherpaout_restricted.txt')
            try:
                if fit_clobber == 'yes' or not already_fit:
                    get_abs(n,z,dir)
                    get_abs_alt(n,z,dir)
                    get_abs_restricted(n,z,dir)
            except:
                error_doc.write(f'{o}\n')
            i += 1


    ##############
    #Time to write out a summary of information we've collected
    #including the number of on-energy counts in each source region
    print('Writing out...')
    header = 'NAME    OBSID    RA     DEC    Z    nH    COUNTS'
    #Edited 7/3/2024
    #np.savetxt(f'{outroot}_data_full.txt', out_full, fmt='%s',delimiter='  ', header=header)
    np.savetxt(f'{outroot}/data_full.txt', out_full, fmt='%s',delimiter='  ', header=header)
    #End edit

    no_match_mask  = np.ones(len(counts),dtype=bool)
    for i, value in enumerate(counts):
        if value == 'NO MATCH':
            no_match_mask[i]= False
    out_counts_only = out_full[no_match_mask,::]
    #Edited 7/3/2024
    #np.savetxt(f'{outroot}_data_full_matches_only.txt', out_counts_only, fmt='%s',delimiter='  ', header=header)
    np.savetxt(f'{outroot}/data_full_matches_only.txt', out_counts_only, fmt='%s',delimiter=',', header=header)
    #End edit

    print('Analyzing fit outputs...')

    ####################
    #Now we run the collate script to collate all the data and make full csvs
    #For each fit
    models = ['', 'alt', 'res']
    for model in models:
        if model == 'alt' or model == 'alternate':
            model_ending_1 = '_alt'
        elif model == 'res' or model == 'restricted':
            model_ending_1 = '_res'
        else:
            model_ending_1 = ''
        print(f'Fitting with model {model}')
        #Edited 7/3/2024
        #min_abs_dir = f'{outroot}_min_abs'
        min_abs_dir = f'{outroot}/min_abs{model_ending_1}'
        #End edit
        data_full_collated_min_abs = collate(data_dir,outroot,chaser_path,True, model)
        data_full_collated = collate(data_dir,outroot,chaser_path,False, model)
        num_columns = data_full_collated_min_abs.shape[1]

        ####################
        #add cosmo calculations and compton thick check to the full csvs made by collate
        #has to be done for both full data and min_abs

        #full data:
        full_lum_arr = []
        full_lum_err_arr = []
        full_OIII_arr = []
        full_OIII_err_arr = []
        full_ratio_arr = []
        full_ratio_err_arr = []
        #full_bID_arr = []
        full_compton_thick_arr = []
        for i in range(len(data_full_collated[::,0])):
            z = data_full_collated[i,-3]
            xflux = data_full_collated[i,8]
            xflux_err = data_full_collated[i,10]

            lum, lum_err = cosmo_calc(z,xflux,xflux_err)
            #Edit 7/3/2024: Temporarily commenting out, since no chaser file
            
            #flux_doc = 'OIII_fluxes.csv'
            
            name = data_full_collated[i,-6]
            
            #OIII_flux, OIII_flux_err,bID = lookup_oiii(flux_doc,name,chaser_path)

            OIII_flux, OIII_flux_err = get_OIII(name, coords_df)
            ratio,ratio_err, compton_thick = get_ratio(OIII_flux, OIII_flux_err, xflux, xflux_err)
            
            #append to the arrays
            #full_bID_arr.append(bID)
            
            full_lum_arr.append(lum)
            full_lum_err_arr.append(lum_err)
            
            full_OIII_arr.append(OIII_flux)
            full_OIII_err_arr.append(OIII_flux_err)
            
            full_ratio_arr.append(ratio)
            full_ratio_err_arr.append(ratio_err)
            full_compton_thick_arr.append(compton_thick)

        '''
        data_full_collated = np.column_stack((data_full_collated,full_lum_arr,full_lum_err_arr,full_OIII_arr,full_OIII_err_arr,full_ratio_arr,full_ratio_err_arr,full_bID_arr))

        header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,CXO name,RA,Dec,Z,galactic nH,counts,exposure time (ks),observation cycle,count rate (c/s),RA offset (deg),dec offset,offset,luminosity,luminosity error,[OIII] flux,[OIII] flux error,Fx/F[OIII],Fx/F[OIII] error,SDSS best ID'
        '''
        data_full_collated = np.column_stack((data_full_collated,full_lum_arr,full_lum_err_arr,full_OIII_arr,full_OIII_err_arr,full_ratio_arr,full_ratio_err_arr, full_compton_thick_arr))

        header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,Soft flux,fluxsoft error plus,fluxsoft error minus,Medium flux,fluxmed error plus,fluxmed error minus,Hard flux,fluxhard error plus,fluxhard error minus,Sum flux,fluxsum error plus,fluxsum error minus,Test Statistic,Ce,Cv,CXO name,RA,Dec,Z,galactic nH,counts,luminosity,luminosity error,Flux_OIII_5006,Flux_OIII_5006_err,Fx/F[OIII],Fx/F[OIII],compton thick'
        #End temporary edit
        
        #Edited 7/3/2024
        #np.savetxt(f'{outroot}_allinfo_full_withratio.csv',data_full_collated,fmt='%s',delimiter=',',header=header)
        np.savetxt(f'{outroot}/allinfo_full_withratio{model_ending_1}.csv',data_full_collated,fmt='%s',delimiter=',',header=header)
        #End edit

        #min_abs:
        min_lum_arr = []
        min_lum_err_arr = []
        min_OIII_arr = []
        min_OIII_err_arr = []
        min_ratio_arr = []
        min_ratio_err_arr = []
        #min_bID_arr = []
        min_compton_thick_arr = []
        for i in range(len(data_full_collated_min_abs[::,0])):
            z = data_full_collated_min_abs[:, -3]
            xflux = data_full_collated_min_abs[i,8]
            xflux_err = data_full_collated_min_abs[i,10]

            lum, lum_err = cosmo_calc(z,xflux,xflux_err)

            #Edited 7/3/2024: temporary edit because no chaser
            
            #flux_doc = 'OIII_fluxes.csv'
            
            name = data_full_collated_min_abs[:, -6]
            
            #OIII_flux, OIII_flux_err,bID = lookup_oiii(flux_doc,name,chaser_path)
            OIII_flux, OIII_flux_err = get_OIII(name, coords_df)

            ratio,ratio_err,compton_thick = get_ratio(OIII_flux, OIII_flux_err, xflux, xflux_err)
            
            #append to the arrays
            #min_bID_arr.append(bID)
            
            min_lum_arr.append(lum)
            min_lum_err_arr.append(lum_err)
            
            min_OIII_arr.append(OIII_flux)
            min_OIII_err_arr.append(OIII_flux_err)
            
            min_ratio_arr.append(ratio)
            min_ratio_err_arr.append(ratio_err)
            min_compton_thick_arr.append(compton_thick)
            
            

        '''
        data_full_collated_min_abs = np.column_stack((data_full_collated_min_abs,min_lum_arr,min_lum_err_arr,min_OIII_arr,min_OIII_err_arr,min_ratio_arr,min_ratio_err_arr,min_bID_arr))

        header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,CXO name,RA,Dec,Z,galactic nH,counts,exposure time (ks),observation cycle,count rate (c/s),RA offset (deg),dec offset,offset,luminosity,luminosity error,[OIII] flux,[OIII] flux error,Fx/F[OIII],Fx/F[OIII] error,SDSS best ID'
        '''
        data_full_collated_min_abs = np.column_stack((data_full_collated_min_abs,min_lum_arr,min_lum_err_arr,min_OIII_arr,min_OIII_err_arr,min_ratio_arr,min_ratio_err_arr, min_compton_thick_arr))

        header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,Soft flux,fluxsoft error plus,fluxsoft error minus,Medium flux,fluxmed error plus,fluxmed error minus,Hard flux,fluxhard error plus,fluxhard error minus,Sum flux,fluxsum error plus,fluxsum error minus,Test Statistic,Ce,Cv,CXO name,RA,Dec,Z,galactic nH,counts,luminosity,luminosity error,Flux_OIII_5006,Flux_OIII_5006_err,Fx/F[OIII],Fx/F[OIII],compton thick'
        #End temporary edit
        
        np.savetxt(f'{min_abs_dir}/{outroot_text}_min_abs_allinfo_full_withratio{model_ending_1}.csv',data_full_collated_min_abs,fmt='%s',delimiter=',',header=header)


    ####################
    #Make the stats table
    print('Making Stat Table')
    obsid_data = np.loadtxt(f'{outroot}/allinfo_full_withratio.csv',dtype='str',delimiter=',')[::,0]

    out = make_spreadsheet(data_dir,obsid_data)
    statsheader = 'obsid,Ce,Cv,DOF,stat'
    statsheader += ',Ce restricted,Cv restricted,DOF restricted,stat restricted'
    statsheader += ',Ce alt,Cv alt,DOF alt,stat alt'
    statsheader += ',P(alt vs main),P(main vs res),P(alt vs res)'
    np.savetxt(f'{outroot}/stats.csv',out,fmt='%s',delimiter = ',',header = statsheader)


    ####################
    #Determine best model for all targets
    print('Finding best models.')
    best_models = get_best_model(data_dir, yes_matches)


    ####################
    #Write out final data
    print('Writing final stats.')
    try:
        os.system(f'mkdir {outroot}/final_data')
    except:
        pass

    main = pd.read_csv(f'{data_dir}/allinfo_full_withratio.csv', dtype=str)
    alt = pd.read_csv(f'{data_dir}/allinfo_full_withratio_alt.csv', dtype=str)
    res = pd.read_csv(f'{data_dir}/allinfo_full_withratio_res.csv', dtype=str)

    final_data = pd.DataFrame(columns=main.columns)

    #Find which model best fits an obsid and use that info in the final table
    for i in range(len(yes_matches)):
        if best_models[i]=='res':
            df=res
        elif best_models[i]=='alt':
            df=alt
        else:
            df=main
            #main but also includes errors

        selected_row = df.loc[df['# ObsID']==yes_matches[i]]
        selected_row.insert(0, 'model', best_models[i])
        
        final_data = pd.concat([final_data, selected_row], ignore_index=True)

    #Move model to beginning of csv
    final_data.insert(1, 'model', final_data.pop('model'))

    #Find targets unabsorbed in their best models
    best_unabsorbed = is_best_unabsorbed(outroot, yes_matches, best_models)
    final_data.insert(1, 'unabsorbed', best_unabsorbed)

    #Identify nans and save to csv
    final_data = final_data.replace(np.nan, 'NaN', regex=True)

    final_data.to_csv(f'{outroot}/final_data/final_info_full.csv', index=False)

    #Save just the minimally absorbed targets, excluding compton thick ones
    min_abs_final = final_data.loc[(final_data['unabsorbed']==True) & (final_data['compton thick']=='False')]

    min_abs_final = min_abs_final.reset_index(drop=True)
    min_abs_final.to_csv(f'{outroot}/final_data/final_info_min_abs_full.csv', index=False)

    with open(f'{outroot}/final_data/final_min_abs_list.txt', 'w') as final_min_abs_file:
        final_min_abs_file.write('#The following sources are unabsorbed in their best model:')
        for id, row in min_abs_final.iterrows():
            final_min_abs_file.write(f"\n{row['CXO name']}")

            #Move files from relevant data directory to final resting place
            model=min_abs_final['model'][id]
            if model == 'alt' or model == 'alternate':
                model_ending_2 = '_alt'
            elif model == 'res' or model == 'restricted':
                model_ending_2 = '_restricted'
            else:
                model_ending_2 = ''

            move_to_min_abs(row['# ObsID'],f'{outroot}/final_data',data_dir, model_ending_2)
    
    #Identify compton thick sources
    print('Finding compton thick targets.')
    compton = final_data.loc[final_data['compton thick']==True]
    with open(f'{outroot}/final_data/final_compton_list.txt', 'w') as compton_file:
        compton_file.write('#The following sources are compton thick:')
        for id, name in enumerate(compton['CXO name']):
            final_min_abs_file.write(f"\n{name}")

    #Find the triply unabsorbed targets, ignoring compton thick sources; this is sort of a silly thing.
    print('Finding triply unabsorbed targets.')
    unabsorbed_list = list(set(get_triply_unabsorbed(outroot))-set(compton['# ObsID']))

    with open(f'{outroot}/final_data/triply_unabsorbed_list.txt', 'w') as triply_unabsorbed_file:
        triply_unabsorbed_file.write('#The following obsids contain sources which are unabsorbed in all models:')
        for i in range(len(unabsorbed_list)):
            triply_unabsorbed_file.write(f'\n{unabsorbed_list[i]}')

    print('Finished')
    print('Examine error logs for errors encountered')

    #Gmail broke being able to send emails in this manner
    #At a later date, want to replace gmail with a different email provider service
    #Google is a stupid head
    '''
    #send email to notify
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "codereporting1@gmail.com"  # Enter your address
    receiver_email = "slarner@wesleyan.edu"  # Enter receiver address
    password = "Password12345!"
    message = f"Full process completed without error"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
    '''


if __name__ == '__main__':
    try:
        main()

    except Exception as e:
        '''
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "codereporting1@gmail.com"  # Enter your address
        receiver_email = "slarner@wesleyan.edu"  # Enter receiver address
        password = "Password12345!"
        message = f"Main in full process failed with exception {e}."

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
        '''
        raise e
