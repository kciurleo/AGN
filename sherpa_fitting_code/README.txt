First, activate heasarc and ciao in that order, e.g.:

	hea
	ciao

Then change directory to the one with all code, e.g.

	cd /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/

Check that all header names for chaser path etc are correct (e.g. Name, ObsID_num, etc). Then run using:

	python [file] [data_dir] [out_root] [coords_path] [chaser_path] [nh_clobber] [wav_clobber] [spec_clobber] [bkg clobber] [fit_clobber]

E.g. if you don\'92t have a chaser file:

	python /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/full_process_sherpa_bxa.py /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/data /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/data /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/testcoords.csv 'no' 'yes' 'yes' 'yes' 'yes' 'yes'

Or for the full data

	python /Users/kciurleo/Documents/kciurleo/AGN/sherpa_fitting_code/full_process_sherpa_bxa.py /opt/pwdata/katie/csc2.1 /opt/pwdata/katie/csc2.1 /Users/kciurleo/Documents/kciurleo/AGN/csvs/full_process_input.csv 'no' 'no' 'no' 'no' 'no' 'no'