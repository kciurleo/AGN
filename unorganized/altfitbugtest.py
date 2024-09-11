import os
import numpy as np
import pandas as pd
import sys

sys.path.append('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code')

os.chdir('/Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code')

import best_model

final_list=pd.read_csv('/opt/pwdata/katie/csc2.1/data_full.txt', skiprows=1, delimiter='  ',names=['NAME','OBSID','RA', 'DEC', 'Z', 'nH', 'COUNTS'])
dude=final_list.loc[final_list['COUNTS']!='NO MATCH']
obsids=dude["OBSID"]

models=best_model.get_best_model('/opt/pwdata/katie/csc2.1','/opt/pwdata/katie/csc2.1',obsids)
dude['model']=models
print(len(dude.loc[dude['model']=='alt']))