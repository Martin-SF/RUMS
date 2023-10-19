import EcoMug as em  # findable when setting PYTHONPATH to build folder
import numpy as np
from numba import vectorize
# import py_library.simulate_lib as slib  # this import caused problems on some systems
import config as cfg
import proposal as pp
from importlib import reload
import math
import random

reload(cfg)

MU_MINUS_MASS_squared_GeV = (pp.particle.MuMinusDef().mass/1000)**2

# calculating momentum of muon for given energy
@vectorize(nopython=True)
def calculate_momentum_vectorized_GeV(energy): 
    return np.sqrt(energy * energy - MU_MINUS_MASS_squared_GeV)



gen = em.EcoMug()
gen.SetUseSky()  # plane surface generation
gen.SetSkySize((0, 0))  # x and y size of the plane
gen.SetSkyCenterPosition((0, 0, 0))  # (x,y,z) position of the center of the plane
gen.SetSeed(cfg.EcoMug_seed)

if cfg.min_E!='':
    gen.SetMinimumMomentum(calculate_momentum_vectorized_GeV(int(float(cfg.min_E))))
if cfg.max_E!='':
    gen.SetMaximumMomentum(calculate_momentum_vectorized_GeV(int(float(cfg.max_E))))
if cfg.param=='gaisser':
    gen.SetDifferentialFluxGaisser()
elif cfg.param=='guan':
    gen.SetDifferentialFluxGuan()

# Ecomug wants altitude angle not azimuth (i couldnt find where this is actually documented lol)
if cfg.max_theta!='':
    min_theta_EcoMug = 90-cfg.max_theta
    gen.SetMinimumTheta(np.radians(min_theta_EcoMug))
if cfg.min_theta!='':
    max_theta_EcoMug = 90-cfg.min_theta
    gen.SetMaximumTheta(np.radians(max_theta_EcoMug))


H = abs(cfg.detector_bottom_depth)
angle_shift = 3/2*np.pi
# pos = 0
# pos = [0,0,0]
def Ecomug_generate(_):
    # reload(cfg)
    # print(cfg_max_theta)
    if cfg.param=='std':
        gen.Generate()
    else:
        gen.GenerateFromCustomJ()
    
    charge = gen.GetCharge()
    p = gen.GetGenerationMomentum()
    phi = gen.GetGenerationPhi()
    # pos = gen.GetGenerationPosition()  # pos will be generated here
    # EcoMug wants altitude angle not azimuth angle, which is getting converted to "standard" here
    theta = angle_shift - gen.GetGenerationTheta()

    # calculate new muon position, so that the muon flies directly on the detector
    r1 = math.tan(theta) * H
    x = r1 * math.cos(phi)
    y = r1 * math.sin(phi)

    # distribute the muons evenly on a target circle around the detector
    angle = random.uniform(0, 2 * math.pi)
    # r2 = random.uniform(0, cfg.radius_target_circle)
    r2 = cfg.radius_target_circle * math.sqrt(random.uniform(0, 1)) # 74.1, 74.3, 74.2s
    # r2 = np.sqrt(np.random.rand()) * cfg.radius_target_circle  # 76.9, 75.5, 74.6s
    x = x + r2 * math.cos(angle)
    y = y + r2 * math.sin(angle)


    # pos = [x, y, 0]
    z = 0
    return (x, y, z, p, theta, phi, charge)
