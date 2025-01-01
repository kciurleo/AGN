import numpy as np
from astropy.io import fits
import glob
import os

# Load the FITS file
base='/opt/pwdata/katie/SDSS/DR17/'
os.chdir(base)
files=glob.glob('*fits')

for filename in files:
    hdulist = fits.open(filename)

    # Extract data
    data = hdulist[1].data
    flux = data['flux']
    loglam = data['loglam']
    ivar = data['ivar']

    wavelength = 10**loglam  # Convert log10(wavelength) to wavelength in Angstroms

    # Create a new FITS header
    hdu = fits.PrimaryHDU(flux)
    header = hdu.header
    header['CRVAL1'] = wavelength[0]  # Starting wavelength
    header['CDELT1'] = wavelength[1] - wavelength[0]  # Wavelength step
    header['CRPIX1'] = 1  # Reference pixel
    header['CTYPE1'] = 'LINEAR'  # Linear wavelength scale
    hdu.header = header

    # Save the new FITS file
    new_filename = f'{base}CONVERTED_{filename}'
    hdu.writeto(new_filename, overwrite=True)

    print(f"Converted file saved as {new_filename}")
