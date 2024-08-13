# This py file deals with the fact that wavdetect seems to fail in Seth's code for some reason.

import glob
import os
from ciao_contrib.runtool import *

def unglob(list): #unglob reformats files matched with the glob command
    list = list[0]
    list = str(list)
    list = list.strip('[]')
    list = list.strip("''")
    return list

def detect(dir): #detect is used to run fluximage and wavdetect in sequence on an obsid
    #needs a level 2 directory with a chandra evt2 file
    print('fluximaging')
    fluximage.punlearn()
    print(dir)
    evt = glob.glob(f'{dir}/*evt2*')
    print(evt)
    evt = unglob(evt)
    print(evt)
    '''
    fluximage.infile=evt
    fluximage.outroot = f'{dir}/detect'
    fluximage.bands = '0.3:7.5:2.3'
    fluximage.psfecf=0.9 #one sigma of 2D gaussian (see 'running wavdetect')
    fluximage.clobber = 'yes'
    fluximage.verbose = 5
    print(fluximage)
    fluximage()
    '''
    os.system(f'Fluximage infile={evt} outroot={dir}/detect bands="0.3:7.5:2.3" psfecf=0.9 clobber="yes" verbose = 4')

    print('wavdetecting')

    wavdetect.punlearn()
    print(wavdetect)
    img = glob.glob(f'{dir}/*thresh.img')
    img = unglob(img)
    wavdetect.infile = img
    psf = glob.glob(f'{dir}/*thresh.psfmap')
    psf = unglob(psf)
    '''
    wavdetect.psffile = psf
    wavdetect.outfile = f'{dir}/detect_src.fits'
    wavdetect.imagefile = f'{dir}/detect_imgfile.fits'
    wavdetect.regfile = f'{dir}/detect_src.reg'
    wavdetect.defnbkgfile = f'{dir}/detect_nbgd.fits'
    wavdetect.scellfile = f'{dir}/detect_scell.fits'
    wavdetect.clobber = 'yes'
    wavdetect.verbose = 5
    print(wavdetect)
    wavdetect()
    '''
    os.system(f'wavdetect infile={img} psffile={psf} outfile={dir}/detect_src.fits scales="2.0 4.0" imagefile={dir}/detect_imgfile.fits regfile={dir}/detect_src.reg defnbkgfile={dir}/detect_nbgd.fits scellfile={dir}/detect_scell.fits clobber="yes" verbose=4')


data_dir="/opt/pwdata/katie/csc2.1"
#data_dir='/Users/kciurleo/Documents/kciurleo/temporary_variable_run'

obsids = os.listdir(data_dir)
#obsids = ['4854']
failures = []
second_half = obsids[int(len(obsids)/2):]

this_one=['404']

for obsid in this_one:
    print(f'Wavdetecting {obsid}')
    try:
        dir = f'{data_dir}/{obsid}/primary'
        detect(dir)
        print('Success')

    except:
        print('Failure')
        failures.append(obsid)


print(f'Failures: {failures}')