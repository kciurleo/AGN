import pandas as pd
from astropy.visualization import simple_norm
from astropy.coordinates import SkyCoord
from astroquery.skyview import SkyView
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.io import votable
import numpy as np
from matplotlib.patches import Circle


XMM_result = votable.parse_single_table('/Users/kciurleo/Documents/kciurleo/AGN/csvs/XMM_query_result.vot').to_table().to_pandas()
XMM_result.rename(columns={'ra_2':'cscra', 'dec_2':'cscdec'}, inplace=True)
xmm_for_casjobs=XMM_result.drop_duplicates()

#xmm_for_casjobs.to_csv('/Users/kciurleo/Downloads/XMMforcasjobs.csv', index=False)

#All matches within 15 arcsec
falseprobtest = pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/falsematchtest.csv')

#Get rid of any duplicates with the exact same spectral target objID
false_uniques=falseprobtest[falseprobtest['targetObjID'] == 0]._append(falseprobtest[falseprobtest['targetObjID'] != 0].drop_duplicates(subset=['targetObjID']))

#Now get rid of anything that has the exat same ras and decs but Would have different specobjids
final=false_uniques.drop_duplicates(subset=['specObjAll_dec','specObjAll_ra', 'ra','dec'])

#Figure out how many obj there are for each ra and dec
duplicate_counts = final.groupby(['ra', 'dec']).size().reset_index(name='num_count')
final = pd.merge(final, duplicate_counts, on=['ra', 'dec'], how='left')

ones=final.loc[final['num_count']==1]
twos=final.loc[final['num_count']==2]
threes=final.loc[final['num_count']==3]

print(f"Number of XMM objects: {len(final.drop_duplicates(subset=['ra','dec']))}")
print(f"Number of XMM objects with 1 unique SDSS within 15 arcsec: {len(ones['ra'])}")
print(f"Number of XMM objects with 2 unique SDSS within 15 arcsec: {len(twos['ra'])/2}")
print(f"Number of XMM objects with 3 unique SDSS within 15 arcsec: {len(threes['ra'])/3}")
print(f"{(15+2)/290*100:.2e} percent are problem children")

def pixel_coords(ra, dec, centerra, centerdec, deg, pix):
    x = pix/2-(ra-centerra)/(deg/pix)
    y = pix/2+(dec-centerdec)/(deg/pix)
    return x, y

def eq_coords(x, y, centerra, centerdec, deg, pix, whattoreturn='both'):
    ra = centerra - (x - pix/2) * (deg / pix)
    dec = centerdec + (y - pix/2) * (deg / pix)

    if whattoreturn == 'both':
        return ra, dec
    elif whattoreturn =='ra':
        return ra
    else:
        return dec

def get_image(ra, dec, deg, pix, title):

    try:
        result = SkyView.get_images(position=SkyCoord(ra=ra[0], dec=dec[0], unit="deg"),
                                    survey='SDSSr',
                                    coordinates='J2000',
                                    pixels=(pix,pix),
                                    height=deg *u.deg,
                                    width=deg*u.deg)
        survey='SDSSr'
    except:
        result = SkyView.get_images(position=SkyCoord(ra=ra[0], dec=dec[0], unit="deg"),
                                    survey='DSS',
                                    coordinates='J2000',
                                    pixels=(pix,pix),
                                    height=deg *u.deg,
                                    width=deg*u.deg)
        survey='DSS'


    image_data = result[0][0].data

    # Display the image
    plt.figure(figsize=(8, 8))
    plt.imshow(image_data, cmap='viridis', origin='lower', norm=simple_norm(image_data, 'sqrt'))
    plt.colorbar(label='Intensity')
    colors = ['black','red','blue']

    #SDSS guys
    for i in range(len(ra)):
        newra, newdec = pixel_coords(ra[i], dec[i], ra[0], dec[0], deg, pix)
        plt.scatter(newra, newdec, marker='o', s=100, edgecolor=colors[i], facecolor='none', label=f'SDSS ({ra[i]}, {dec[i]})', alpha=0.75)
        xmmra, xmmdec = pixel_coords(title[0], title[1], ra[0], dec[0], deg, pix)
    
    #XMM guy
    plt.scatter(xmmra, xmmdec, marker='x', s=100, c='black', label=f'XMM {title}')

    #Cone search
    circle = Circle((xmmra,xmmdec), (10/3600)*(pix/deg), edgecolor='limegreen', facecolor='none', label='CSC Cone Search Radius')
    circle2 = Circle((xmmra,xmmdec), (4/3600)*(pix/deg), edgecolor='limegreen', facecolor='none', alpha=0.25)
    
    plt.gca().add_patch(circle)
    plt.gca().add_patch(circle2)

    plt.title(f'{survey} image, XMM coords: {title}')

    #Axes
    ticks=np.arange(0,pix+50, 50)
    raticks=eq_coords(ticks, 0, ra[0], dec[0], deg, pix, 'ra')
    decticks=eq_coords(0, ticks, ra[0], dec[0], deg, pix, 'dec')

    raticks_formatted = [f'{coord:.4f}' for coord in raticks]
    decticks_formatted = [f'{coord:.4f}' for coord in decticks]

    plt.gca().set_xticks(ticks) 
    plt.gca().set_yticks(ticks)
    plt.gca().set_xticklabels(raticks_formatted)
    plt.gca().set_yticklabels(decticks_formatted)

    plt.legend()
    plt.xlabel('RA (degrees)')
    plt.ylabel('Dec (degrees)')
    plt.show(block=False)

#Group the data
groupedtwos = twos.groupby(['ra', 'dec'])
groupedthrees = threes.groupby(['ra', 'dec'])

#Loop over and print
'''
for group_name, group_data in groupedtwos:
    get_image(np.array(group_data['specObjAll_ra']), np.array(group_data['specObjAll_dec']), 1/60, 300, group_name)

for group_name, group_data in groupedthrees:
    get_image(np.array(group_data['specObjAll_ra']), np.array(group_data['specObjAll_dec']), 1/60, 300, group_name)


plt.show()

'''