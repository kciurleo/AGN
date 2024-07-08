#this program will be run after the fitting program is done and will collate
#all the relevant information on the sources into one big csv file
#and when given a list of un absorbed sources it will make one for just them

#deeply sorry if you have to read this, some of my worst work
#written in a fugue state, continuously patched together to make it work

#modified to work with the full process program
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,soft flux,fluxsoft error plus,fluxsoft error minus,med flux,fluxmed error plus,fluxmed error minus,hard flux,fluxhard error plus,fluxhard error minus,sum flux,fluxsum error plus,fluxsum error minus'

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import numpy as np

def move_to_min_abs(obsid,min_abs_dir,data_dir): #copies files for the indicated obsid to the min abs directory
    newdir = f'{min_abs_dir}/{obsid}'
    try:
        os.system(f'mkdir {newdir}')
    except:
        pass

    os.system(f'cp {data_dir}/{obsid}/primary/sherpaout.txt {min_abs_dir}/{obsid}/{obsid}_abs_summary.txt')
    os.system(f'cp {data_dir}/{obsid}/primary/sherpa_data_fit.pdf {min_abs_dir}/{obsid}/{obsid}_sherpa_data_fit.pdf')
    os.system(f'cp {data_dir}/{obsid}/primary/get_abs.save {min_abs_dir}/{obsid}/{obsid}_get_abs.save')


def is_unique(list):
    return len(list) == len(np.unique(list))

#examine logs reads the logs for the sources it is given and makes an array of the
#properites contained within
def examine_logs(min_abs,write_out,data_dir,outroot):
    min_abs_list = []
    outroot_text = outroot.split('/')[-1]
    #min_abs controls if the process is applied to the unabsorbed sources (true) or all (false)
    #write_out controls if the csvs are made
    #probably shouldn't be right now, but its there if you want it
    #this process ripped from log_read.py

    #Edited 7/3/2024
    #min_abs_dir = f'{outroot}_min_abs'
    min_abs_dir = f'{outroot}/min_abs'
    #End edit
    try: #don't want to error out if the directory already exists
        os.system(f'mkdir {min_abs_dir}')
    except:
        pass
    
    #Edited 7/3/2024
    #in_list = np.loadtxt(f'{outroot}_data_full_matches_only.txt',dtype='str',delimiter=',')[::,1]
    in_list = np.loadtxt(f'{outroot}/data_full_matches_only.txt',dtype='str',delimiter=',')[::,1]
    #End edit

    nH_values = []
    nH_error_ups = []
    nH_error_downs = []
    gamma_values = []
    gamma_error_ups = []
    gamma_error_downs = []
    stat_values = []
    xflux_values = []
    xflux_error_ups = []
    xflux_error_downs = []
    flux210_values = []
    flux210_error_ups = []
    flux210_error_downs = []
    fluxsoft_values = []
    fluxsoft_error_ups = []
    fluxsoft_error_downs = []
    fluxmed_values = []
    fluxmed_error_ups = []
    fluxmed_error_downs = []
    fluxhard_values = []
    fluxhard_error_ups = []
    fluxhard_error_downs = []
    fluxsum_values = []
    fluxsum_error_ups = []
    fluxsum_error_downs = []
    test_stat_values = []
    ce_values = []
    cv_values = []

    for obsid in in_list:
        nH_failed = False
        gamma_failed = False
        xflux_failed = False
        flux210_failed = False
        fluxsoft_failed = False
        fluxmed_failed = False
        fluxhard_failed = False
        fluxsum_failed = False
        all_failed = False

        dir = f'{data_dir}/{obsid}/primary'
        try:
            with open(f'{data_dir}/{obsid}/primary/sherpaout.txt','r') as out:
                summary_list = out.read().split('\n')
        except FileNotFoundError:
            summary_list = 'p' #give this a nonsense value so that it trips the excepts and properly documents errors

        #read the nH values and error
        if not all_failed:
            try:
                nH = summary_list[3].split()[0]
            except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                nH = 'ERROR'
                nH_error_up = 'ERROR'
                nH_error_down = 'ERROR'
                nH_failed = True
        if not nH_failed:
            try:
                nH_error_up = summary_list[5].split()[1]
            except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                nH_error_up = 'ERROR'
            try:
                nH_error_down = summary_list[5].split()[0]
            except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                nH_error_down = 'ERROR'

        #add in the check to min_abs
        #just continue if the conditions arent met
        if min_abs:
            if nH_failed or float(nH) >= 0.05:
                continue
            else:
                min_abs_list.append(obsid)
                move_to_min_abs(obsid,min_abs_dir,data_dir)

        if not min_abs or float(nH) < 0.05:
        #if either the function was not called to run on min_abs or
        #the function was called to run on min_abs and the obsid which is
        #being processed has a nH less than the set thershold
            nH_values.append(nH)
            nH_error_ups.append(nH_error_up)
            nH_error_downs.append(nH_error_down)

            #read the gamma values and errors
            if not all_failed:
                try:
                    gamma = summary_list[7].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    gamma = 'ERROR'
                    gamma_error_up = 'ERROR'
                    gamma_error_down = 'ERROR'
                    gamma_failed = True
            if not gamma_failed:
                try:
                    gamma_error_up = summary_list[9].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    gamma_error_up = 'ERROR'
                try:
                    gamma_error_down = summary_list[9].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    gamma_error_down = 'ERROR'
            gamma_values.append(gamma)
            gamma_error_ups.append(gamma_error_up)
            gamma_error_downs.append(gamma_error_down)

            #read the cstat values
            if not all_failed:
                try:
                    cstat = summary_list[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    cstat = 'ERROR'
                stat_values.append(cstat)

            #read the .3-7.5 fluxes
            if not all_failed:
                try:
                    xflux = summary_list[11].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    xflux = 'ERROR'
                    xflux_error_up = 'ERROR'
                    xflux_error_down = 'ERROR'
                    xflux_failed = True
            if not xflux_failed:
                try:
                    xflux_error_down = summary_list[11].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    xflux_error_down = 'ERROR'
                try:
                    xflux_error_up = summary_list[11].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    xflux_error_up = 'ERROR'
            xflux_values.append(xflux)
            xflux_error_downs.append(xflux_error_down)
            xflux_error_ups.append(xflux_error_up)

            #read the 2-10 fluxes
            if not all_failed:
                try:
                    flux210 = summary_list[13].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    flux210 = 'ERROR'
                    flux210_error_up = 'ERROR'
                    flux210_error_down = 'ERROR'
                    flux210_failed = True
            if not flux210_failed:
                try:
                    flux210_error_down = summary_list[13].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    flux210_error_down = 'ERROR'
                try:
                    flux210_error_up = summary_list[13].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    flux210_error_up = 'ERROR'
            flux210_values.append(flux210)
            flux210_error_downs.append(flux210_error_down)
            flux210_error_ups.append(flux210_error_up)

            #read the 'soft' fluxes
            if not all_failed:
                try:
                    fluxsoft = summary_list[23].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsoft = 'ERROR'
                    fluxsoft_error_up = 'ERROR'
                    fluxsoft_error_down = 'ERROR'
                    fluxsoft_failed = True
            if not fluxsoft_failed:
                try:
                    fluxsoft_error_down = summary_list[23].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsoft_error_down = 'ERROR'
                try:
                    fluxsoft_error_up = summary_list[23].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsoft_error_up = 'ERROR'
            fluxsoft_values.append(fluxsoft)
            fluxsoft_error_downs.append(fluxsoft_error_down)
            fluxsoft_error_ups.append(fluxsoft_error_up)

            #read the 'medium' fluxes
            if not all_failed:
                try:
                    fluxmed = summary_list[25].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxmed = 'ERROR'
                    fluxmed_error_up = 'ERROR'
                    fluxmed_error_down = 'ERROR'
                    fluxmed_failed = True
            if not fluxmed_failed:
                try:
                    fluxmed_error_down = summary_list[25].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxmed_error_down = 'ERROR'
                try:
                    fluxmed_error_up = summary_list[25].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxmed_error_up = 'ERROR'
            fluxmed_values.append(fluxmed)
            fluxmed_error_downs.append(fluxmed_error_down)
            fluxmed_error_ups.append(fluxmed_error_up)

            #read the 'hard' fluxes
            if not all_failed:
                try:
                    fluxhard = summary_list[27].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxhard = 'ERROR'
                    fluxhard_error_up = 'ERROR'
                    fluxhard_error_down = 'ERROR'
                    fluxhard_failed = True
            if not fluxhard_failed:
                try:
                    fluxhard_error_down = summary_list[27].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxhard_error_down = 'ERROR'
                try:
                    fluxhard_error_up = summary_list[27].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsoft_error_up = 'ERROR'
            fluxhard_values.append(fluxhard)
            fluxhard_error_downs.append(fluxhard_error_down)
            fluxhard_error_ups.append(fluxhard_error_up)

            #read the 'summed' fluxes
            if not all_failed:
                try:
                    fluxsum = summary_list[29].split()[0]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsum = 'ERROR'
                    fluxsum_error_up = 'ERROR'
                    fluxsum_error_down = 'ERROR'
                    fluxsum_failed = True
            if not fluxsum_failed:
                try:
                    fluxsum_error_down = summary_list[29].split()[1]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsum_error_down = 'ERROR'
                try:
                    fluxsum_error_up = summary_list[29].split()[2]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    fluxsum_error_up = 'ERROR'
            fluxsum_values.append(fluxsum)
            fluxsum_error_downs.append(fluxsum_error_down)
            fluxsum_error_ups.append(fluxsum_error_up)

            #read the test statistics
            if not all_failed:
                try:
                    test_stat = summary_list[15]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    test_stat = 'ERROR'
            test_stat_values.append(test_stat)
            if not all_failed:
                try:
                    ce = summary_list[17]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    ce = 'ERROR'
            ce_values.append(ce)
            if not all_failed:
                try:
                    cv = summary_list[19]
                except (IndexError, TypeError, FileNotFoundError, ValueError) as e:
                    cv = 'ERROR'
            cv_values.append(cv)



    if min_abs:
        csv_out = np.column_stack((min_abs_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs, test_stat_values, ce_values, cv_values))
    else:
        csv_out = np.column_stack((in_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs,fluxsoft_values,fluxsoft_error_ups,fluxsoft_error_downs,fluxmed_values,fluxmed_error_ups,fluxmed_error_downs,fluxhard_values,fluxhard_error_ups,fluxhard_error_downs,fluxsum_values,fluxsum_error_ups,fluxsum_error_downs, test_stat_values, ce_values, cv_values))
    header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,soft flux,fluxsoft error plus,fluxsoft error minus,med flux,fluxmed error plus,fluxmed error minus,hard flux,fluxhard error plus,fluxhard error minus,sum flux,fluxsum error plus,fluxsum error minus,Test Statistic,Ce,Cv'

    if write_out:
        if min_abs:
            np.savetxt(f'{min_abs_dir}/{outroot_text}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)
        else:
            #Edited 7/3/2024
            #np.savetxt(f'{outroot}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)
            np.savetxt(f'{outroot}/allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)
            #End edit

    return csv_out


def collate(data_dir,outroot,chaser_path,min_abs_tf):
    #Edited 7/3/2024
    #min_abs_dir = f'{outroot}_min_abs'
    min_abs_dir = f'{outroot}/min_abs'
    #End edit
    header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,soft flux,fluxsoft error plus,fluxsoft error minus,med flux,fluxmed error plus,fluxmed error minus,hard flux,fluxhard error plus,fluxhard error minus,sum flux,fluxsum error plus,fluxsum error minus,Test Statistic,Ce,Cv'
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    outroot_text = outroot.split('/')[-1]

    print('Reading matches document...')
    #Edited 7/3/2024
    #matched_data = np.loadtxt(f'{outroot}_data_full_matches_only.txt', dtype='str', delimiter=',')
    matched_data = np.loadtxt(f'{outroot}/data_full_matches_only.txt', dtype='str', delimiter=',')
    #End edit
    matched_names = matched_data[::,0]
    matched_obsids = matched_data[::,1]
    matched_RAs = matched_data[::,2]
    matched_decs = matched_data[::,3]
    matched_zs = matched_data[::,4]
    matched_nHs = matched_data[::,5]
    matched_counts = matched_data[::,6]

    print('Reading chaser document...')
    #Edit 7/3/2024: temporary bandaid for lack of chaser data
    try:
        chaser_data = np.loadtxt(chaser_path,delimiter=',',dtype='str')
        chaser_obsids = chaser_data[1:,1]
        chaser_exptimes = chaser_data[1:,5] #exposure time needed to calculate count rate, measured in ks
        chaser_cycles = chaser_data[1:,20]
        chaser_RAs = chaser_data[1:,8]
        chaser_decs = chaser_data[1:,9]
    except:
        print('No chaser data found. Ignoring chaser data.')
        chaser_obsids = []
        chaser_exptimes = [] #exposure time needed to calculate count rate, measured in ks
        chaser_cycles = []
        chaser_RAs = []
        chaser_decs = []
    #End edit; all code within try was here previously


    print('Reading logs...')
    csv_out = examine_logs(min_abs_tf,True,data_dir,outroot)

    read_obsids = csv_out[::,0]
    if read_obsids[-1] == '':
        read_obsids = read_obsids[:-1] #hacky way to remove the last blank entry
        csv_out = csv_out[:-1,::]

    #now we need to put the other arrays into the order defined by csv_out
    #initial the ordered arrays
    matched_names_ordered = []
    matched_RAs_ordered = []
    matched_decs_ordered = []
    matched_zs_ordered = []
    matched_nHs_ordered = []
    matched_counts_ordered = []
    chaser_exptimes_ordered = []
    chaser_cycles_ordered = []
    chaser_RAs_ordered = []
    chaser_decs_ordered = []

    for j,read_obsid in enumerate(read_obsids):
        match_matched = False
        chaser_matched = False
        if read_obsid[-1] in alphabet:
            read_obsid_noletter = read_obsid[:-1]
        else:
            read_obsid_noletter = read_obsid

        for i,matched_obsid in enumerate(matched_obsids):
            if matched_obsid == read_obsid:
                match_matched = True
                matched_names_ordered.append(matched_names[i])
                matched_RAs_ordered.append(matched_RAs[i])
                matched_decs_ordered.append(matched_decs[i])
                matched_zs_ordered.append(matched_zs[i])
                matched_nHs_ordered.append(matched_nHs[i])
                matched_counts_ordered.append(matched_counts[i])
                break

        for i,chaser_obsid in enumerate(chaser_obsids):
            if chaser_obsid == read_obsid_noletter:
                chaser_matched = True
                chaser_exptimes_ordered.append(chaser_exptimes[i])
                chaser_cycles_ordered.append(chaser_cycles[i])
                chaser_RAs_ordered.append(chaser_RAs[i])
                chaser_decs_ordered.append(chaser_decs[i])
                break

        #Edited 7/3/2024: temporarily ignoring these exceptions
        '''
        if not match_matched:
            print(f'match not found for {read_obsid} in the matched dataset')
            raise Exception
        if not chaser_matched:
            print(f'match not found for {read_obsid} in the chaser dataset')
            raise Exception
        '''
        #End edit

    #write count rate calculation
    #Edited 7/3/2024: Temporary non-chaser ignoring exceptions
    '''
    try:
        count_rates = [float(matched_counts_ordered[i])/(1000*float(chaser_exptimes_ordered[i])) for i in range(len(matched_counts_ordered))]
    except IndexError as e:
        print(len(matched_counts_ordered))
        print(len(chaser_exptimes_ordered))
        print(len(read_obsids))
        raise e

    #write angle off axis calculation
    ra_offsets = [abs(float(matched_RAs_ordered[i])-float(chaser_RAs_ordered[i])) for i in range(len(chaser_RAs_ordered))]
    dec_offsets = [abs(float(matched_decs_ordered[i])-float(chaser_decs_ordered[i])) for i in range(len(chaser_RAs_ordered))]
    offsets = [(ra_offsets[i]**2 + dec_offsets[i]**2)**(1/2) for i in range(len(ra_offsets))]

    final_csv = np.column_stack((csv_out,matched_names_ordered,matched_RAs_ordered,matched_decs_ordered,matched_zs_ordered,matched_nHs_ordered,matched_counts_ordered,chaser_exptimes_ordered,chaser_cycles_ordered,count_rates,ra_offsets,dec_offsets,offsets))
    header += ',CXO name,RA,Dec,Z,galactic nH,counts,exposure time (ks),observation cycle,count rate (c/s),RA offset (deg),dec offset,offset'
    '''

    final_csv = np.column_stack((csv_out,matched_names_ordered,matched_RAs_ordered,matched_decs_ordered,matched_zs_ordered,matched_nHs_ordered,matched_counts_ordered))
    header += ',CXO name,RA,Dec,Z,galactic nH,counts'
    #End edit

    if min_abs_tf:
        np.savetxt(f'{min_abs_dir}/{outroot_text}_min_abs_allinfo_full.csv',final_csv,fmt='%s',delimiter=',',header=header)
    else:
        #Edited 7/3/2024
        #np.savetxt(f'{outroot}_allinfo_full.csv',final_csv,fmt='%s',delimiter=',',header=header)
        np.savetxt(f'{outroot}/allinfo_full.csv',final_csv,fmt='%s',delimiter=',',header=header)
        #End edit

    return final_csv


if __name__ == '__main__':
    print('Reading inputs...')

    if len(sys.argv) != 5:
        print(f'''Inputs not recognized
    Try: python {sys.argv[0]} [data_dir] [outroot] [chaser_path] [min_abs?]''')
        raise Exception

    data_dir = sys.argv[1]
    outroot = sys.argv[2]
    outroot_text = outroot.split('/')[-1]
    chaser_path = sys.argv[3]

    if 't' in sys.argv[4]:
        min_abs_tf = True
    elif 'f' in sys.argv[4]:
        min_abs_tf = False
    else:
        print('Enter true/false for min abs')
        raise Exception

    collate(data_dir,outroot,chaser_path,min_abs_tf)
