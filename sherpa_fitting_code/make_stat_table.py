#this script reads in the fitting logs and makes a spread sheet of the statistics
#for the fits to the three different models

#then it runs a version of an Ftest using those models
#and adds that to the spreadsheet

import numpy as np
import matplotlib.pyplot as plt
from sherpa.astro.ui import *
import sys

def read_doc(file_path):

    with open(file_path,'r') as file:
        data_list = file.read().split('\n')

    stat = data_list[15]
    Ce = data_list[17]
    Cv = data_list[19]
    dof = data_list[21]

    return stat,Ce,Cv,dof

def run_ftest(stat1,dof1,stat2,dof2):
    return calc_ftest(stat1,dof1,stat2,dof2)

def make_spreadsheet(data_dir,obsid_list):
    Ce_arr = []
    Ce_res_arr = []
    Ce_alt_arr = []

    Cv_arr = []
    Cv_res_arr = []
    Cv_alt_arr = []

    stat_arr = []
    stat_res_arr = []
    stat_alt_arr = []

    dof_arr = []
    dof_res_arr = []
    dof_alt_arr = []

    main_alt_comp_arr = []
    main_res_comp_arr = []
    alt_res_comp_arr = []

    for obsid in obsid_list:
        dir = f'{data_dir}/{obsid}/primary'

        file = f'{dir}/sherpaout.txt'
        alt_file = f'{dir}/sherpaout_alt.txt'
        res_file = f'{dir}/sherpaout_restricted.txt'

        try:
            stat,Ce,Cv,dof = read_doc(file)
        except (FileNotFoundError, IndexError):
            stat,Ce,Cv,dof = ('ERROR','ERROR','ERROR','ERROR')
        try:
            stat_res,Ce_res,Cv_res,dof_res = read_doc(res_file)
        except (FileNotFoundError, IndexError):
             stat_res,Ce_res,Cv_res,dof_res = ('ERROR','ERROR','ERROR','ERROR')
        try:
            stat_alt,Ce_alt,Cv_alt,dof_alt = read_doc(alt_file)
        except (FileNotFoundError, IndexError):
            stat_alt,Ce_alt,Cv_alt,dof_alt = ('ERROR','ERROR','ERROR','ERROR')

        Ce_arr.append(Ce)
        Ce_res_arr.append(Ce_res)
        Ce_alt_arr.append(Ce_alt)

        Cv_arr.append(Cv)
        Cv_res_arr.append(Cv_res)
        Cv_alt_arr.append(Cv_alt)

        stat_arr.append(stat)
        stat_res_arr.append(stat_res)
        stat_alt_arr.append(stat_alt)

        dof_arr.append(dof)
        dof_res_arr.append(dof_res)
        dof_alt_arr.append(dof_alt)

        if 'ERROR' not in (stat,stat_alt,dof,dof_alt):
            main_alt_comp_arr.append(run_ftest(stat,dof,stat_alt,dof_alt))
        else:
            main_alt_comp_arr.append('ERROR')

        if 'ERROR' not in (stat,stat_res,dof,dof_res):
            main_res_comp_arr.append(run_ftest(stat,dof,stat_res,dof_res))
        else:
            main_res_comp_arr.append('ERROR')

        if 'ERROR' not in (stat_alt,stat_res,dof_alt,dof_res):
            alt_res_comp_arr.append(run_ftest(stat_alt,dof_alt,stat_res,dof_res))
        else:
            alt_res_comp_arr.append('ERROR')

    out = np.column_stack((obsid_list,Ce_arr,Cv_arr,dof_arr,stat_arr))
    out = np.column_stack((out,Ce_res_arr,Cv_res_arr,dof_res_arr,stat_res_arr))
    out = np.column_stack((out,Ce_alt_arr,Cv_alt_arr,dof_alt_arr,stat_alt_arr))
    out = np.column_stack((out,main_alt_comp_arr,main_res_comp_arr,alt_res_comp_arr))

    return out

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Enter {sys.argv[0]} [outroot] [data_dir]')
        raise Exception

    outroot = sys.argv[1]
    data_dir = sys.argv[2]

    obsid_data = np.loadtxt(f'{outroot}_allinfo_full_withratio.csv',dtype='str',delimiter=',')[::,0]

    out = make_spreadsheet(data_dir,obsid_data)
    header = 'obsid,Ce,Cv,DOF,stat'
    header += ',Ce restricted,Cv restricted,DOF restricted,stat restricted'
    header += ',Ce alt,Cv alt,DOF alt,stat alt'
    header += ',P(alt vs main),P(main vs res),P(alt vs res)'
    np.savetxt(f'{outroot}_stats.csv',out,fmt='%s',delimiter = ',',header = header)
