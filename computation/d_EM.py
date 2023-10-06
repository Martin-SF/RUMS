# %%
import os, sys
os.chdir(os.path.dirname(__file__))
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import proposal as pp
from importlib import reload

import py_library.my_plots_library as plib
import py_library.simulate_lib as slib
import py_library.stopwatch as stopwatch
import config as config_file

from distributed import Client, LocalCluster
from dask.distributed import performance_report
# import dask.bag as db
import dask.dataframe as dd
client = Client("localhost:8786")  # local client


#%
# generating Muons with Ecomug into HDF
############################################################
############################################################
############################################################
t = stopwatch.stopwatch(title='generating ecomug muons', selfexecutiontime_micros=0, time_unit='s', return_results=True)
import d_EM_lib as emo
client.upload_file('d_EM_lib.py')
client.upload_file('config.py')
reload(emo)
reload(slib)
reload(plib)
reload(stopwatch)
reload(config_file)

print(f'generating {config_file.file_name}')
N_tasks = config_file.N_tasks
chunksize = round((config_file.STATISTICS/N_tasks))+1

# local variable!!!
# workaround für viele tasks 
tmphdf = config_file.hdf_folder+'tmp.hdf'
df = pd.DataFrame()
df['0'] = np.zeros(config_file.STATISTICS)
df.to_hdf(tmphdf, key=f'main', format='table')

with performance_report(filename="dask-report_EM.html"):
    ddf = dd.read_hdf(tmphdf, key='main', columns=['0'], chunksize=chunksize)
    b = ddf.to_bag()
    # b = db.from_sequence(map(bool, arr), partition_size=chunksize)  # 1/2 slowdown
    b = b.map(emo.Ecomug_generate)
    b = b.to_dataframe()
    t.task('calculate muons with EcoMug', True)
    results = client.compute(b, pure=False).result()

os.remove(tmphdf)

t.task('post calculations')
results_array = np.array(results)

# muon_pos = np.zeros(shape=(config_file.STATISTICS, 3))
# muon_pos = np.array(list(results_array[:, 0]))
muon_x = np.array(results_array[:,0], dtype=float)
muon_y = np.array(results_array[:,1], dtype=float)
muon_z = np.array(results_array[:,2], dtype=float)
muon_p = np.array(results_array[:,3], dtype=float)
muon_theta = np.array(results_array[:, 4], dtype=float)
muon_phi = np.array(results_array[:, 5], dtype=float)
muon_charge = np.array(results_array[:, 6], dtype=np.int8)

muon_e = slib.calculate_energy_vectorized_GeV(muon_p)  # faster than for loop


# import random
# import math

# # Parameters of the circle
# radius = 10 * 1e2  # You can change the radius as needed

# H = abs(config_file.detector_pos[2]) - config_file.detector_height/2

# # Generate random points on the circle
# x_points = []
# y_points = []
# for i in range(config_file.STATISTICS):
#     # Generate a random angle in radians
#     angle = random.uniform(0, 2 * math.pi)
#     r = random.uniform(0, radius)

#     # Calculate the coordinates of the point on the circle
#     x = r * math.cos(angle)
#     y = r * math.sin(angle)

#     # if (config_file.calibrate == True):
#     #     H = config_file.detector_height

#     # angle_2 = (muon_phi[i] + np.pi) % (2*np.pi)
#     angle_2 = muon_phi[i]
#     R_new = np.tan(muon_theta[i]) * H

#     x = x + R_new * math.cos(angle_2)
#     y = y + R_new * math.sin(angle_2)
#     x_points.append(x)
#     y_points.append(y)


# muon_phi = (muon_phi + np.pi) % (2*np.pi)
df = pd.DataFrame()
# df['pos_x'] = muon_pos[:, 0]
# df['pos_y'] = muon_pos[:, 1]
# df['pos_x'] = np.array(x_points)
# df['pos_y'] = np.array(y_points)
df['pos_x'] = muon_x
df['pos_y'] = muon_y

# df['pos_z'] = muon_pos[:, 2]
df['pos_z'] = muon_z
# df['position'] = muon_pos
df['momentum'] = muon_p
df['energy'] = muon_e
df['theta'] = muon_theta
df['phi'] = muon_phi
df['charge'] = muon_charge
t.task('write to HDF')

file_path = config_file.hdf_folder+config_file.file_name

# Check if the file exists
if os.path.exists(file_path):
    # If it exists, delete it
    os.remove(file_path)

df.to_hdf(file_path, key=f'main', format='table')

elapsed_time_total = t.stop(True)['TOTAL']
# muonen_1e7_time = ( (elapsed_time_total/config_file.STATISTICS)*int(1e7))/(60*60)
# print(f'bei aktuellem xmom würden 1e7 muonen {muonen_1e7_time:2.1f} Stunden dauern')
print(f'Total time: {elapsed_time_total/(60):2.1f} min')