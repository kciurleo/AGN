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
    evt = glob.glob(f'{dir}/*evt2*')
    evt = unglob(evt)
    fluximage.infile=evt
    fluximage.outroot = f'{dir}/detect'
    fluximage.bands = '0.3:7.5:2.3'
    fluximage.psfecf=0.9 #one sigma of 2D gaussian (see 'running wavdetect')
    fluximage.clobber = 'yes'
    fluximage.verbose = 5
    #print(fluximage)
    fluximage()

    print('wavdetecting')

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
    wavdetect.verbose = 4
    wavdetect()


data_dir="/opt/pwdata/katie/csc2.1"

obsids = ['12024'] #os.listdir(data_dir)
failures = []

for obsid in obsids:
    print(f'Wavdetecting {obsid}')
    try:
        dir = f'{data_dir}/{obsid}/primary'
        detect(dir)
        print('Success')

    except:
        print('Failure')
        failures.append(obsid)


print(f'Failures: {failures}')