#this program will be run after the fitting program is done and will collate
#all the relevant information on the sources into one big csv file
#and when given a list of un absorbed sources it will make one for just them

#this script is meant to run on the restricted and alt models
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus'

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def move_to_min_abs(obsid,min_abs_dir,data_dir): #copies files for the indicated obsid to the min abs directory
    newdir = f'{min_abs_dir}/{obsid}'
    try:
        os.system(f'mkdir {newdir}')
    except:
        pass
    os.system(f'cp {data_dir}/{obsid}/primary/sherpaout.txt {min_abs_dir}/{obsid}/{obsid}_abs_summary.txt')
    os.system(f'cp {data_dir}/{obsid}/primary/sherpa_data_fit.pdf {min_abs_dir}/{obsid}/{obsid}_sherpa_data_fit.pdf')
    os.system(f'cp {data_dir}/{obsid}/primary/get_abs.save {min_abs_dir}/{obsid}/{obsid}_get_abs.save')


#examine logs reads the logs for the sources it is given and makes an array of the
#properites contained within
#for alt model
def examine_logs_alt(min_abs,write_out,data_dir,outroot):
    min_abs_list = []
    outroot_text = outroot.split('/')[-1]
    #min_abs controls if the process is applied to the unabsorbed sources (true) or all (false)
    #write_out controls if the csvs are made
    #probably shouldn't be right now, but its there if you want it
    #this process ripped from log_read.py

    min_abs_dir = f'{outroot}_min_abs_alt'
    try: #don't want to error out if the directory already exists
        os.system(f'mkdir {min_abs_dir}')
    except:
        pass

    in_list = np.loadtxt(f'{outroot}_data_full_matches_only.txt',dtype='str',delimiter=',')[::,1]

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

    for obsid in in_list:
        nH_failed = False
        gamma_failed = False
        xflux_failed = False
        flux210_failed = False
        all_failed = False
        test_failed = False
        dir = f'{data_dir}/{obsid}/primary'
        try:
            with open(f'{data_dir}/{obsid}/primary/sherpaout_alt.txt','r') as out:
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



    if min_abs:
        csv_out = np.column_stack((min_abs_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs))
    else:
        csv_out = np.column_stack((in_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs))
    header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus'

    if write_out:
        if min_abs:
            np.savetxt(f'{min_abs_dir}/{outroot_text}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)
        else:
            np.savetxt(f'{outroot}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)

    return csv_out

#examine logs reads the logs for the sources it is given and makes an array of the
#properites contained within
#for restricted model
def examine_logs_res(min_abs,write_out,data_dir,outroot):
    min_abs_list = []
    outroot_text = outroot.split('/')[-1]
    #min_abs controls if the process is applied to the unabsorbed sources (true) or all (false)
    #write_out controls if the csvs are made
    #probably shouldn't be right now, but its there if you want it
    #this process ripped from log_read.py

    min_abs_dir = f'{outroot}_min_abs_res'
    try: #don't want to error out if the directory already exists
        os.system(f'mkdir {min_abs_dir}')
    except:
        pass

    in_list = np.loadtxt(f'{outroot}_data_full_matches_only.txt',dtype='str',delimiter=',')[::,1]


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

    for obsid in in_list:
        nH_failed = False
        gamma_failed = False
        xflux_failed = False
        flux210_failed = False
        all_failed = False
        test_failed = False
        dir = f'{data_dir}/{obsid}/primary'
        try:
            with open(f'{data_dir}/{obsid}/primary/sherpaout_restricted.txt','r') as out:
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



    if min_abs:
        csv_out = np.column_stack((min_abs_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs))
    else:
        csv_out = np.column_stack((in_list,stat_values,nH_values,nH_error_ups,nH_error_downs,gamma_values,gamma_error_ups,gamma_error_downs,xflux_values,xflux_error_ups,xflux_error_downs,flux210_values,flux210_error_ups,flux210_error_downs))
    header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus'

    if write_out:
        if min_abs:
            np.savetxt(f'{min_abs_dir}/{outroot_text}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)
        else:
            np.savetxt(f'{outroot}_allinfo.csv',csv_out,fmt='%s',delimiter=',',header=header)

    return csv_out


def collate(data_dir,outroot,chaser_path,min_abs_tf,model):
    min_abs_dir = f'{outroot}_min_abs'
    header = 'ObsID,Cstat,nH,nH error plus,nH error minus,gamma,gamma error plus,gamma error minus,0.3-7.5 flux,xflux error plus,xflux_error_minus,2-10 flux,flux210 error plus,flux210 error minus,Test Statistic,Ce,Cv'
    alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    outroot_text = outroot.split('/')[-1]

    print('Reading matches document...')
    matched_data = np.loadtxt(f'{outroot}_data_full_matches_only.txt', dtype='str', delimiter=',')
    matched_names = matched_data[::,0]
    matched_obsids = matched_data[::,1]
    matched_RAs = matched_data[::,2]
    matched_decs = matched_data[::,3]
    matched_zs = matched_data[::,4]
    matched_nHs = matched_data[::,5]
    matched_counts = matched_data[::,6]

    print('Reading chaser document...')
    chaser_data = np.loadtxt(chaser_path,dtype='str',delimiter=',')
    chaser_obsids = chaser_data[1:,1]
    chaser_exptimes = chaser_data[1:,5] #exposure time needed to calculate count rate, measured in ks
    chaser_cycles = chaser_data[1:,20]
    chaser_RAs = chaser_data[1:,8]
    chaser_decs = chaser_data[1:,9]

    if model == 'alt':
        csv_out = examine_logs_alt(min_abs_tf,True,data_dir,outroot)
    elif model == 'res':
        csv_out = examine_logs_res(min_abs_tf,True,data_dir,outroot)
    else:
        print('Unknown model')
        raise Exception

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
        chaser_match = False
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

        for i,chaser_obsid in enumerate(chaser_obsids):
            if chaser_obsid == read_obsid_noletter:
                chaser_matched = True
                chaser_exptimes_ordered.append(chaser_exptimes[i])
                chaser_cycles_ordered.append(chaser_cycles[i])
                chaser_RAs_ordered.append(chaser_RAs[i])
                chaser_decs_ordered.append(chaser_decs[i])
                break

        if not match_matched:
            print(f'match not found for {read_obsid} in the matched dataset')
            raise Exception
        if not chaser_matched:
            print(f'match not found for {read_obsid} in the chaser dataset')
            raise Exception

    #write count rate calculation
    count_rates = [float(matched_counts_ordered[i])/(1000*float(chaser_exptimes_ordered[i])) for i in range(len(matched_counts_ordered))]

    #write angle off axis calculation
    ra_offsets = [abs(float(matched_RAs_ordered[i])-float(chaser_RAs_ordered[i])) for i in range(len(chaser_RAs_ordered))]
    dec_offsets = [abs(float(matched_decs_ordered[i])-float(chaser_decs_ordered[i])) for i in range(len(chaser_RAs_ordered))]
    offsets = [(ra_offsets[i]**2 + dec_offsets[i]**2)**(1/2) for i in range(len(ra_offsets))]

    final_csv = np.column_stack((csv_out,matched_names_ordered,matched_RAs_ordered,matched_decs_ordered,matched_zs_ordered,matched_nHs_ordered,matched_counts_ordered,chaser_exptimes_ordered,chaser_cycles_ordered,count_rates,ra_offsets,dec_offsets,offsets))
    header += ',CXO name,RA,Dec,Z,galactic nH,counts,exposure time (ks),observation cycle,count rate (c/s),RA offset (deg),dec offset,offset'

    if min_abs_tf:
        np.savetxt(f'{min_abs_dir}/{outroot_text}_min_abs_allinfo_full_{model}.csv',final_csv,fmt='%s',delimiter=',',header=header)
    else:
        np.savetxt(f'{outroot}_allinfo_full_{model}.csv',final_csv,fmt='%s',delimiter=',',header=header)

    return final_csv


if __name__ == '__main__':
    print('Reading inputs...')

    if len(sys.argv) != 6:
        print(f'''Inputs not recognized
    Try: python {sys.argv[0]} [data_dir] [outroot] [chaser_path] [min_abs?] [model]''')
        raise Exception

    data_dir = sys.argv[1]
    outroot = sys.argv[2]
    outroot_text = outroot.split('/')[-1]
    chaser_path = sys.argv[3]
    model = sys.argv[5]

    if model != 'alt' and model != 'res':
        print('Unknown model')
        raise Exception

    if 't' in sys.argv[4]:
        min_abs_tf = True
    elif 'f' in sys.argv[4]:
        min_abs_tf = False
    else:
        print('Enter true or false for min abs')
        raise Exception

    min_abs_dir = f'{outroot}_min_abs'

    collate(data_dir,outroot,chaser_path,min_abs_tf,model)
