#%%
import traceback
import proposal as pp
import numpy as np
import py_library.my_plots_library as plib
import py_library.stopwatch as stopwatch
# import py_library.simulate_lib as slib
# import os, sys
import config as cfg
from importlib import reload

reload(cfg)  # important for up to date variables in worker


detector = pp.geometry.Cylinder(
    pp.Cartesian3D(cfg.detector_pos),
    inner_radius = 0,
    radius = cfg.detector_radius,
    height = cfg.detector_height
)

pp.RandomGenerator.get().set_seed(cfg.PROPOSAL_seed)
pp.InterpolationSettings.nodes_utility = 1000
pp.InterpolationSettings.tables_path = cfg.pp_tables_path

prop_plus = pp.Propagator(
    particle_def=pp.particle.MuPlusDef(),
    path_to_config_file=cfg.path_to_config_file
)

prop_minus = pp.Propagator(
    particle_def=pp.particle.MuMinusDef(),
    path_to_config_file=cfg.path_to_config_file
)

init_state = pp.particle.ParticleState()
init_state.type = 13  # type for muons+

# position = np.array([0,0,0])
# init_state.position = pp.Cartesian3D(position)

def pp_propagate(input):
    energy_init = input[0]
    theta = input[1]
    phi = input[2]
    charge = input[3]
    pos_x = input[4]
    pos_y = input[5]
    pos_z = input[6]
    # current_muon = (f'{position}, (1, {phi}, {theta}), {energy_init*1000}MeV, {charge}\n')
    # print(f'{current_muon}')
    # print(os.getcwd())
    # t1 = stopwatch(
    # title='inside propagation loop', time_unit='µs',
    # selfexecutiontime_micros=0.7)  # total time when hit target 38 µs

    # t1.task('give muon to proposal')  # 17% of loop time
    # init_state.momentum = momentum  # MeV
    energy_init = energy_init*1000   # GeV into MeV
    init_state.energy = energy_init
    init_state.position = pp.Cartesian3D(np.array([pos_x, pos_y, pos_z]))
    init_state.direction = pp.Cartesian3D(pp.Spherical3D(1, phi, theta))

    try:
        if (charge == 1):
            track = prop_plus.propagate(
                init_state, *cfg.propagate_settings)
        else:
            track = prop_minus.propagate(
                init_state, *cfg.propagate_settings)
    except Exception as e:
        print(e)
        traceback.print_exc()
        # current_muon = (f'[], {position}, (1, {phi}, {theta}), ' +
        #     f'{energy} MeV, {charge}\n')
        # print(f'failed muon: {current_muon}')
        # muons.append(current_muon)

    # t1.task('did geometry hit?')  # 4% of loop time
    # point2 = plib.pp_get_pos(track.track()[-1].position)

    # if (point2[2] <= cfg.detector_bottom_depth or
    if (track.hit_geometry(detector) or 
        cfg.every_particle_hits_detector):
        hit_detector = True

        # t1.task('write propagate array and write to array')  # 14% loop time
        distance_at_track_end = track.track_propagated_distances()[-1]
        energy_at_track_end = track.track_energies()[-1]

        # t1.task('add start points to array')  # 41% of loop time TODO
        point1 = plib.pp_get_pos(init_state.position)
        point2 = plib.pp_get_pos(track.track()[-1].position)
        point1x = point1[0]
        point1y = point1[1]
        point1z = point1[2]
        point2x = point2[0]
        point2y = point2[1]
        point2z = point2[2]
        theta_i_raw = theta
    else:
        # print(track.track()[-1].position.y)
        # print(input)
        hit_detector = False
        distance_at_track_end = None
        energy_at_track_end = None
        point1x = None
        point1y = None
        point1z = None
        point2x = None
        point2y = None
        point2z = None
        theta_i_raw = None


    # print(position, energy_init, theta, phi, charge)
    # hit_detector = False  
    # t1.stop()

    return (hit_detector, distance_at_track_end, energy_at_track_end, 
    energy_init, point1x, point1y, point1z, point2x, point2y, point2z, theta_i_raw)
