import numpy as np
import json

###########################################################
###########################################################
###########################################################
# Plot and misc settings

show_plots = True
if (show_plots):
    show_or_multiplot = 'show'
else:
    show_or_multiplot = ''
print_results = False
silent = True




###########################################################
###########################################################
###########################################################
# Dask Distributed settings

# set of "tasks" into which the task should be divided. 
# optimal: number of real cores -1
#   (1 core for the dask-scheduler so that it doesn't crash)
N_tasks = 100
N_tasks = 23  #  (phobos = 24-1 = 23) 

# hdf_folder = 'data_hdf/'
hdf_folder = '/scratch/mschoenfeld/data_hdf/'




###########################################################
###########################################################
###########################################################
# EcoMug (d_EM.py and d_EM_lib.py)

EcoMug_seed = int(np.random.random()*1000)

# muon parametrisation
param = 'guan'
param = 'std'
param = 'gaisser'  # bachelor thesis results value


# min / max theta (in degrees)
# Ecomug wants altitude angle not azimuth (i couldnt find where this is documented...) conversion is in d_EM_lib.py

# bachelor thesis results value (but the ecomug distribution was flipped!!!)

# min_theta = ''
min_theta = '0'  # bachelor thesis results value

# max_theta = ''
# max_theta = '30'  # bachelor thesis results value
max_theta = '60'


# amount of muons generated
# phobos runtime
# Ecomug:   1e7:30min   ; 1e6: 30s
# PROPOSAL: 1e7:60min(?); 1e6: 6min
STATISTICS = '1e7'  # bachelor thesis results value
STATISTICS = '1e4'
STATISTICS = '1e5'
STATISTICS = '1e6'


# min Energy (in GeV)
min_E = ''  # use standard value
min_E = '6e2'  # bachelor thesis results value

# max Energy (in GeV)
max_E = ''  # use standard value (999 GeV momentum)
max_E = '1e6'  # unuseable with gaisser
max_E = '1e3'  # good for min_E = ''
max_E = '2e5'  # bachelor thesis results value
max_E = '3e5' 




###########################################################
###########################################################
############################################################
# Proposal (d_pp.py and d_pp_lib.py)

PROPOSAL_seed = int(np.random.random()*10000)
# pp_tables_path = "/scratch/mschoenfeld/tables_path"
pp_tables_path = "/tmp"

# which file to propagate
PP_config = 'sandstein.json'
PP_config = 'stdrock_perf_tests.json'
PP_config = 'stdrock_perf_tests2ndtiefe.json'
PP_config = 'KH_748m_alt.json'
PP_config = "config_cylinder-huge.json"
PP_config = 'kirchhellen1.json'
PP_config = 'KH_800m.json'
PP_config = 'kirchhellen_AVG.json'
PP_config = 'kirchhellen_AVG_840m.json'
PP_config = 'kirchhellen_AVG_3D.json'
PP_config = 'kirchhellen_AVG_3D_840m.json'


v_cut = ''
v_cut = 0.0008
v_cut = 0.001  # bachelor thesis results value

multiple_scattering = 'HighlandIntegral'
multiple_scattering = 'Moliere'
multiple_scattering = 'noscattering'
multiple_scattering = 'Highland'  # bachelor thesis results value




###########################################################
###########################################################
###########################################################
# Detector settings (does not infuence your jsons automatically! )

# debuggin option. proposal module will save all particles regardless if they hid the detector.
every_particle_hits_detector = False

detector_pos = (0, 0, -125400)
detector_height = 10 * 1e2
detector_radius = 5


# PROPOSAL: max_distance, min_energy, hierarchy_condition
# propagate_settings = (1e20, 0, 10)  # bachelor thesis results value
safety_puffer_propagate_puffer = 2
max_propagate_distance = np.tan(np.radians(int(max_theta))) * ((detector_pos[2] - detector_height/2) * safety_puffer_propagate_puffer) 
propagate_settings = (abs(int(max_propagate_distance)), 0, 10)  # 3D

safety_puffer_propagate_puffer = 1
radius_target_circle = np.tan(np.radians(int(max_theta))) * (detector_height * safety_puffer_propagate_puffer)  # 1.1 for deflection safety?

detector_area = 75  # bachelor thesis results value
# detector_area = detector_area * calibrate_which_get_detected
# this is the artificial detector area covering all incoming muons
artificial_detector_area = np.pi * radius_target_circle**2


### calibrate todos
# calibrate useless .... (discarded)
# change to calibrate json
# change detector_pos
# set calibrate to True (disables repositioning in ecomug)
# calibrate = False

# if (calibrate == True):
#     PP_config = 'kirchhellen_AVG_3D_calibrate.json'

#     STATISTICS = '1e5'

#     min_E = '6e3'
#     min_E = '6e4'
#     min_E = '6e8'
#     max_E = '2e9'

#     # detector_pos = (0, 0, -500)  # calibrate

# (11932.0) of 1e+06 (1.193)% detector hits | min(E_i) at detector = 600.0 GeV
# calibrate_which_get_detected = 0.01235




###########################################################
###########################################################
###########################################################
# really miscellaneous and nothing to configure actually


pp_config_string = f'vcut={v_cut}_{multiple_scattering}'
path_to_config_file = "config/"+PP_config

# refresh PP_config json with newest v_cut and multiple_scattering
with open(path_to_config_file, 'r+') as file:
    data = json.load(file)
    data['global']['cuts']['v_cut'] = v_cut
    data['global']['scattering']['multiple_scattering'] = multiple_scattering

    file.seek(0)        # <--- should reset file position to the beginning.
    json.dump(data, file, indent=4)
    file.truncate()     # remove remaining part

file_name = f'EcoMug_{STATISTICS}_{param}_min{min_E}_max{max_E}_{max_theta}deg_3D_1.1.hdf'
file_name_results = f'{PP_config}_{pp_config_string}_{file_name}'

STATISTICS = int(float(STATISTICS))