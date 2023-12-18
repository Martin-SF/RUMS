import numpy as np
import json
import os

###########################################################
###########################################################
###########################################################
# Plot and misc settings

show_plots = True
if (show_plots):
    show_or_multiplot = 'show'
else:
    show_or_multiplot = ''
silent = False 
silent = True  # stopwatch prints silent

# for identifiying different runs
subfolder = 'ms_6/'
subfolder = 't2_r0_1/'
subfolder = 't3_r1percent_3/'
subfolder = 'test4/'  # gamma = 1
subfolder = 'gaisser_plots/'  # gamma = 0.6
subfolder = 'test3/'  # gamma = 0.6
subfolder = 'gamma06/'  # gamma = 0.6
subfolder = 'gamma06_v2/'  # gamma = 0.6

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
EcoMug_seed = 1909

# muon parametrisation
param = 'guan'
param = 'std'
gaisser_gamma = 0.6
param = 'gaisser'  # bachelor thesis results value
param = 'gaisser_samp'  # bachelor thesis results value



# min / max theta (in degrees) azimuth angle
# (Ecomug expects altitude angle not azimuth angle, I couldnt find where this is actually documented...)
# the thetas are getting automatically converted in d_EM_lib.py
# the bachelor thesis results are flawed because of this

# min_theta = ''
min_theta = 0  # bachelor thesis results value   # 3D settings
# min_theta = 75  #
# min_theta = 56  #

# max_theta = ''
# max_theta = 30  # bachelor thesis results value
max_theta = 60  # 3D settings
# max_theta = 75  # 3D settings
# max_theta = 56  # 3D settings


# amount of muons generated
# phobos runtime
# Ecomug:   1e7:1.5min ;1e6: 15s
# PROPOSAL: 1e7:60min  ;1e6: 6min (highland) (moliere 2x)
STATISTICS = '1e8'
STATISTICS = '2e7'
STATISTICS = '1e3'
STATISTICS = '5e5'
STATISTICS = '1e2'
STATISTICS = '1e5'
STATISTICS = '1e6'
STATISTICS = '1e4'
STATISTICS = '1e7'  # bachelor thesis results value


# min Energy (GeV)
min_E = ''  # use standard value
min_E = '6e2'  # bachelor thesis results value
min_E = '8'  # 3D optimized
min_E = '730'  # 3D optimized

# max Energy (GeV)
max_E = ''  # use standard value (999 GeV momentum)
max_E = '1e6'  # unuseable with gaisser
max_E = '1e3'  # good for min_E = ''
max_E = '2e5'  # bachelor thesis results value
max_E = '4e3' 
max_E = '3e5' 
max_E = '1e6'  # new energy threshord for gaisser_samp




###########################################################
###########################################################
############################################################
# PROPOSAL (d_pp.py and d_pp_lib.py)

PROPOSAL_seed = 1909
pp_tables_path = "/tmp/"
pp_tables_path = "/scratch/mschoenfeld/tables_path"

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
PP_config = 'kirchhellen_AVG_3D_840m_nodet.json'
PP_config = 'kirchhellen_AVG_3D_840m.json'


v_cut = ''
v_cut = 0.0008
v_cut = 0.001  # bachelor thesis results value

multiple_scattering = 'HighlandIntegral'
multiple_scattering = 'noscattering'
multiple_scattering = 'Moliere'
multiple_scattering = 'Highland'  # bachelor thesis results value
multiple_scattering = 'MoliereInterpol'




###########################################################
###########################################################
###########################################################
# detector settings (does NOT change your PP_config json automatically!)

# debugging option. proposal module will save all particles regardless if they hit the detector.
every_particle_hits_detector = False

# borehole detector
detector_pos = (0, 0, -125400)
detector_radius = 5  # 5cm
detector_height = 10 * 1e2  # 10m
detector_bottom_depth = detector_pos[2] - detector_height/2


# PROPOSAL: max_distance, min_energy, hierarchy_condition
# propagate_settings = (1e20, 0, 10)  # bachelor thesis results value
buffer_max_propagate_distance = 1.3
max_propagate_distance = int((abs(detector_bottom_depth) * buffer_max_propagate_distance) / np.cos(np.radians(max_theta)))
propagate_settings = (max_propagate_distance, 0, 10)  # 3D

buffer_radius_target_circle = 1
detector_target_circle = np.tan(np.radians(max_theta)) * (detector_height * buffer_radius_target_circle)  # 1.1 for deflection safety?

# tests of the effect of changes of the angle due to multiple_scattering and stochastic_deflection
# radius_target_circle = 55 * 1e2       # 0.0102  % of all particles missing  # test: t3_r1percent_1
# radius_target_circle = 18.5 * 1e2     # 0.101   % of all particles missing
# radius_target_circle = 17.32 * 1e2    # 0.117   % of all particles missing (for max_theta=60 and detector_height=10m)
# radius_target_circle = 8.75 * 1e2     # 1.002   % of all particles missing  # test: t3_r1percent_2
# radius_target_circle = 4.709 * 1e2    # 10.002  % of all particles missing
# radius_target_circle = 1.94655 * 1e2  # 50.0001 % of all particles missing  # test: t3_r1percent_3

detector_area = 75  # bachelor thesis results value
# this is the artificial two dimensional projected detector area covering all incoming muons
detector_artificial_area = np.pi * detector_target_circle**2




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

if param == "gaisser_samp":
    param_ = param+"_"+str(gaisser_gamma)
else:
    param_ = param

file_name_ = f'EcoMug_{STATISTICS}_{param_}_min{min_E}_max{max_E}_{max_theta}deg_3D.hdf'
file_name_results = f'{subfolder}{PP_config}_{pp_config_string}_{file_name_}'
file_name = f'{subfolder}{file_name_}'

if not os.path.exists(f'figures/{subfolder}'):
    os.makedirs(f'figures/{subfolder}')

if not os.path.exists(f'{hdf_folder}{subfolder}'):
    os.makedirs(f'{hdf_folder}{subfolder}')


STATISTICS = int(float(STATISTICS))


def gaisser(theta, E, gamma=2.7):
    return 0.14*E**(-gamma)*(
                    1    /(1 + 1.1 * E * np.cos(theta) / (115))
                  + 0.054/(1 + 1.1 * E * np.cos(theta) / (850))
                )
    
# this is the function with which the events were sampled
gaisser_samp = lambda theta, E: gaisser(theta, E, gaisser_gamma)
# this is the distribution we want
gaisser_wanted = lambda theta, E: gaisser(theta, E, 2.7)


from scipy.integrate import dblquad
def get_weights(mode, energy, theta):
    # calculating the total flux makes it possible to make the sampled function a probability distribution
    total_flux_samp, total_flux_samp_unc = (2*np.pi*sol for sol in dblquad(gaisser_samp,
        float(min_E), float(max_E),
        lambda E: np.radians(float(min_theta)), lambda E: np.radians(float(max_theta))
        ))
    # print(f"muons_per_cm2_per_second sampled: {total_flux_samp:.3e} +- {total_flux_samp_unc:.3e}")

    if (mode == "counts"):
        # calculating the total flux makes it possible to make the sampled function a probability distribution
        total_flux_wanted, total_flux_wanted_unc = (2*np.pi*sol for sol in dblquad(gaisser_wanted,
            float(min_E), float(max_E),
        lambda E: np.radians(float(min_theta)), lambda E: np.radians(float(max_theta))
        ))
        weights_numbers = gaisser_wanted(theta, energy) / (gaisser_samp(theta, energy)/total_flux_samp) * (1/total_flux_wanted)
        return weights_numbers
    elif (mode == "flux"):
        weights_flux = (
            gaisser_wanted(theta, energy)/(gaisser_samp(theta, energy)/total_flux_samp)
            * (1/len(energy))
        )
        return weights_flux
    else:
        print(f"get_weights: ERROR! only mode  - counts - or - flux - available")