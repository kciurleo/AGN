import math as m
import pandas as pd

def get_OIII(name, coords_df):
    #Assuming coords_df also has the OIII fluxes
    try:
        #Get the first instance of the name
        row=coords_df.loc[coords_df['CSC21P_name'] == name].head(1)
    except:
        return 'ERROR', 'ERROR'
    
    try:
        OIII = float(row['Flux_OIII_5006'].iloc[0])
    except:
        OIII = 'ERROR'
    try:
        OIIIerr =float(row['Flux_OIII_5006_Err'].iloc[0])
    except:
        OIIIerr = 'ERROR'
    
    return OIII, OIIIerr

def get_ratio(OIII_flux,OIII_flux_err,xflux,xflux_err):
    try:
        xflux = float(xflux)
        xflux_err = float(xflux_err)
        OIII_flux = float(OIII_flux)/1E17 #convert to ergs
        OIII_flux_err = float(OIII_flux_err)/1E17
        ratio = xflux/OIII_flux
        ratio_error = ratio * m.sqrt((xflux_err/xflux)**2 + (OIII_flux_err/OIII_flux)**2)
        if ratio - ratio_error < 1:
            compton_thick = True
        else:
            compton_thick = False

        return ratio,ratio_error,compton_thick
    
    except (ZeroDivisionError, TypeError, ValueError) as e:
        return 'ERROR','ERROR',"ERROR"

if __name__ == '__main__':
    df=pd.read_csv('/Users/kciurleo/Documents/kciurleo/AGN/csvs/obsids_seyferts.csv')
    get_OIII('2CXO J134736.4+173404', df)
