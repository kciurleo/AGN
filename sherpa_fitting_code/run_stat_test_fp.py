from cstat_goodness import *
import numpy as np
from sherpa.astro.ui import *


#because of sherpa weirdness, requires the data to have just been plotted
#using plot_fit (or plot_fit_resid?)
def calc_cstat(C):
    #the tolerance for the infinite sums
    eps = 1E-7


    #read in data, sort through it
    data = get_fit_plot()

    model_data = data.modelplot
    expected_counts = model_data.y


    cei_arr = []
    cvi_arr = []
    for mu in expected_counts:
        cei = Cei(mu,eps)
        cvi = Cvi(mu,eps)

        cei_arr.append(cei)
        cvi_arr.append(cvi)


    Ce = sum(cei_arr)
    Cv = sum(cvi_arr)

    stat = abs(Ce - C) / np.sqrt(Cv)

    return stat, Ce, Cv

if __name__ == '__main__':
    from get_abs_sherpa_bxa import *
    import os

    get_abs(0.0375,0.2201888,'../x-ray/all_sources_copy/19563/primary')

    print(calc_cstat())
