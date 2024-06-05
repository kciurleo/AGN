import numpy as np
from astropy.io import fits
print('working')
filename='/Users/kciurleo/Documents/kciurleo/unorganized/CSC2.1p_OIR_SDSSspecmatch.fits'
hdr=fits.getheader(filename)
print(hdr)