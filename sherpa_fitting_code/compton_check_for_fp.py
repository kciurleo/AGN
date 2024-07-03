#contains the functions which get the [oIII] flux and perform the compton
#thick check
#called by full_process

import numpy as np
import math as m

#flux doc is the document in which the OIII fluxes for the sources have been recorded
#name is the name of the source in the CXO naming style
    #as would be found in the CSC
#chaser path is the path from cwd to the chaser file detailing the information about the downloaded obsids

def lookup_oiii(flux_doc,name,chaser_path):
    cross_match = np.load('../Sloan_Chandra_Cross_Matching/x-ray_download/CSC2-SDSSDR15_FinalXmatch.npy')
    cross_name_arr = cross_match[1:,0]
    cross_bID_arr = cross_match[1:,13]

    OIII_doc = np.loadtxt(flux_doc,delimiter=',',dtype='str')
    OIII_bID_arr = OIII_doc[1:,0]
    OIII_flux_arr = OIII_doc[1:,1].astype('float')
    OIII_flux_err_arr = OIII_doc[1:,2].astype('float')

    chaser = np.loadtxt(chaser_path,delimiter=',',dtype='str')

    match = False
    for i, cross_name in enumerate(cross_name_arr):
        if cross_name == name:
            cross_row = i
            match = True
            break

    if not match:
        print(f'No match finding name: {name} in crossmatch')
        #raise Exception
        return -1, -1, -1


    cross_bID = cross_bID_arr[cross_row]
    match = False
    for i, OIII_bID in enumerate(OIII_bID_arr):
        if cross_bID == OIII_bID:
            OIII_row = i
            match = True
            break
    if not match:
        print(f'No match finding bID: {cross_bID} in OIII doc')
        #raise Exception
        return -1, -1, cross_bID

    return OIII_flux_arr[OIII_row],OIII_flux_err_arr[OIII_row],cross_bID

def calc_ratio(OIII_flux,OIII_flux_err,xflux,xflux_err):
    try:
        xflux = float(xflux)
        xflux_err = float(xflux_err)
        OIII_flux = float(OIII_flux)/1E17
        OIII_flux_err = float(OIII_flux_err)/1E17
        ratio = xflux/OIII_flux
        ratio_error = ratio * m.sqrt((xflux_err/xflux)**2 + (OIII_flux_err/OIII_flux)**2)
        return ratio,ratio_error
    except (ZeroDivisionError, TypeError, ValueError) as e:
        return 'ERROR','ERROR'

def main():
    flux,flux_err = lookup_oiii('OIII_fluxes.csv','2CXO J142841.1+323222','../x-ray/all_sources_copy/chaser_oldbatch.csv')
    ratio, ratio_error = calc_ratio(flux,flux_err,3.16201989229133E-13,3.10937094769703E-14)
    print(f'Xflux/[OIII] flux = {ratio} +/- {ratio_error}')

if __name__ == '__main__':
    main()
