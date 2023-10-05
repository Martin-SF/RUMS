# from EcoMug_pybind11.build import EcoMug as em
import EcoMug as em  # findable when setting PYTHONPATH to build folder
import numpy as np
from numba import vectorize
# import py_library.simulate_lib as slib  # this import caused problems on some systems
import config as config_file
import proposal as pp
from importlib import reload
import math
import random

reload(config_file)

MU_MINUS_MASS_squared_GeV = (pp.particle.MuMinusDef().mass/1000)**2

# calculating momentum of muon for given energy
@vectorize(nopython=True)
def calculate_momentum_vectorized_GeV(energy): 
    return np.sqrt(energy * energy - MU_MINUS_MASS_squared_GeV)



gen = em.EcoMug()
gen.SetUseSky()  # plane surface generation
gen.SetSkySize((0, 0))  # x and y size of the plane
gen.SetSkyCenterPosition((0, 0, 0))  # (x,y,z) position of the center of the plane
gen.SetSeed(config_file.EcoMug_seed)

if config_file.min_E!='':
    gen.SetMinimumMomentum(calculate_momentum_vectorized_GeV(int(float(config_file.min_E))))
if config_file.max_E!='':
    gen.SetMaximumMomentum(calculate_momentum_vectorized_GeV(int(float(config_file.max_E))))
if config_file.param=='gaisser':
    gen.SetDifferentialFluxGaisser()
elif config_file.param=='guan':
    gen.SetDifferentialFluxGuan()

# Ecomug wants altitude angle not azimuth (i couldnt find where this is actually documented lol)

if config_file.max_theta!='':
    min_theta_EcoMug = 90-int(config_file.max_theta)
    gen.SetMinimumTheta(np.radians(min_theta_EcoMug))
if config_file.min_theta!='':
    max_theta_EcoMug = 90-int(config_file.min_theta)
    gen.SetMaximumTheta(np.radians(max_theta_EcoMug))




H = abs(config_file.detector_pos[2] - config_file.detector_height/2)
degree_shift = 3/2*np.pi
# pos = 0
# pos = [0,0,0]
def Ecomug_generate(_):
    if config_file.param=='std':
        gen.Generate()
    else:
        gen.GenerateFromCustomJ()
    
    charge = gen.GetCharge()
    p = gen.GetGenerationMomentum()
    phi = gen.GetGenerationPhi()
    # theta = gen.GetGenerationTheta()
    theta = degree_shift - gen.GetGenerationTheta()

    # pos = gen.GetGenerationPosition()  # 7 µs

    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, config_file.radius_target_circle)

    # Calculate the coordinates of the point on the circle
    x = r * math.cos(angle)
    y = r * math.sin(angle)

    # to target
    angle_2 = phi
    R_new = np.tan(theta) * H

    x = x + R_new * math.cos(angle_2)
    y = y + R_new * math.sin(angle_2)

    # theta = degree_shift - theta

    # pos = [x, y, 0]
    z = 0
    return (x, y, z, p, theta, phi, charge)
