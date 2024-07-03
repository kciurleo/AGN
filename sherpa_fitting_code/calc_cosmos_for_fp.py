#contains the function which does the Cosmology calculations needed
#called by full_process

import subprocess
import math as m

def cosmo_calc(z,flux,f_err):
    H0 = '69.6'
    WM = '0.286'
    WV = '0.714'
    z = str(z)

    try:
        #Edited 7/3/2024, assuming cwd is directory which contains cosmo_calc.py
        #cosmo = subprocess.run(['python', '../low_abs_analysis_code/cosmo_calc.py', z, H0, WM, WV], stdout=subprocess.PIPE)
        cosmo = subprocess.run(['python', 'cosmo_calc.py', z, H0, WM, WV], stdout=subprocess.PIPE)
        #End edit
        cosmo = cosmo.stdout.decode('utf-8')
        DL = float(cosmo.split('\n')[3])
        #need to get DL in cm
        DL *= 3.08568E24
        lum = (DL**2)*4*m.pi*float(flux)
        lum_err = (DL**2)*4*m.pi*float(f_err)
        return lum, lum_err

    except (ValueError, IndexError) as e:
        return 'NONE', 'NONE'

if __name__ == '__main__':
    lum,lum_err = cosmo_calc(0.04264033,5.65642679318644E-14,6.47704602355821E-15)
    print(f'{lum} erg/s +/- {lum_err}')
