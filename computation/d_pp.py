# %%
# print(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import os, sys
from uncertainties import ufloat
from importlib import reload
import py_library.my_plots_library as plib
import py_library.stopwatch as stopwatch
import py_library.simulate_lib as slib
import proposal as pp
from distributed import Client, LocalCluster
from dask.distributed import performance_report
import dask.dataframe as dd
import dask.bag as db
import config as config_file


plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['axes.labelsize'] = 14
plt.rcParams.update({'figure.dpi':70})
# os.chdir(os.path.dirname(__file__))  # wichtig wenn nicht über ipython ausgeführt
client = Client("localhost:8786") # phobos
FLOAT_TYPE = np.float64


print(f'{config_file.file_name} | N_tasks = {config_file.N_tasks}')
# %
######################################################################
######################################################################
t1 = stopwatch.stopwatch(
    title='full proposal init and simulation parallized with dask',
    time_unit='s')
t1.task('initialize proposal, making interpol tables')

import d_pp_lib as proper
client.upload_file('d_pp_lib.py')
client.upload_file('config.py')
reload(proper)
reload(stopwatch)
reload(plib)
reload(config_file)
print(f'PROPOSAL config = {config_file.PP_config}, {config_file.pp_config_string}')

STATISTICS = len(pd.read_hdf(
    config_file.hdf_folder+config_file.file_name, key=f'main', columns=['charge']))
chunksize = round((STATISTICS/config_file.N_tasks))+1

meta={
    'hit_detector': bool, 
    'distances_f_raw': FLOAT_TYPE, 
    'energies_f_raw': FLOAT_TYPE, 
    'energies_i_raw': FLOAT_TYPE, 
    'point1x_raw': FLOAT_TYPE, 
    'point1y_raw': FLOAT_TYPE, 
    'point1z_raw': FLOAT_TYPE, 
    'point2x_raw': FLOAT_TYPE,
    'point2y_raw': FLOAT_TYPE,
    'point2z_raw': FLOAT_TYPE
}

t1.task('propagating', True)

# just for reference
# future = client.submit(func, big_data)    # bad

# big_future = client.scatter(big_data)     # good
# future = client.submit(func, big_future)  # good
# # own approach
# ddf = client.scatter(ddf)
# dfb = ddf.result().to_bag()


# dfb = client.map(proper.pp_propagate, db.from_delayed(dfb) ) #27s
# dfb = client.map(proper.pp_propagate, dfb) #27s

with performance_report(filename="dask-report_PP.html"):
    ddf = dd.read_hdf(config_file.hdf_folder+config_file.file_name, key='main',
                    columns=['energy', 'theta', 'phi', 'charge', 'pos_x', 'pos_y', 'pos_z'], chunksize=chunksize)
    dfb = ddf.to_bag()

    dfb = dfb.map(proper.pp_propagate) #27s
    ddfr = dfb.to_dataframe(meta=meta)
    # ddfr.to_hdf(config_file.hdf_folder+'results_raw_'+config_file.file_name, key=f'main', format='table')
    results = client.compute(ddfr, pure=False).result()

t1.stop(config_file.silent)
# %
t2 = stopwatch.stopwatch(title='processing of results')
t2.task('post processing 0')
# todo die nachbereitung mit dask arrays beschleunigen
######################################################################
######################################################################


hit_detector = np.array(results['hit_detector'], dtype=bool)
distances_f_raw = np.array(results['distances_f_raw'], dtype=FLOAT_TYPE)
energies_f_raw = np.array(results['energies_f_raw'], dtype=FLOAT_TYPE)
energies_i_raw = np.array(results['energies_i_raw'], dtype=FLOAT_TYPE)
point1x_raw = np.array(results['point1x_raw'], dtype=FLOAT_TYPE)
point1y_raw = np.array(results['point1y_raw'], dtype=FLOAT_TYPE)
point1z_raw = np.array(results['point1z_raw'], dtype=FLOAT_TYPE)
point2x_raw = np.array(results['point2x_raw'], dtype=FLOAT_TYPE)
point2y_raw = np.array(results['point2y_raw'], dtype=FLOAT_TYPE)
point2z_raw = np.array(results['point2z_raw'], dtype=FLOAT_TYPE)

counter = int(sum(hit_detector))  # len von allen die True sind
energies_f = np.zeros(counter, dtype=FLOAT_TYPE)
energies_i = np.zeros(counter, dtype=FLOAT_TYPE)
distances_f = np.zeros(counter, dtype=FLOAT_TYPE)
start_points = np.zeros(shape=(counter, 3), dtype=FLOAT_TYPE)
end_points = np.zeros(shape=(counter, 3), dtype=FLOAT_TYPE)
start_end_points = np.zeros(shape=(counter*2, 3), dtype=FLOAT_TYPE)

t2.task('post processing 1')
i2 = 0
for i in range(STATISTICS):
    if hit_detector[i] == True:
        energies_f[i2] = energies_f_raw[i]
        energies_i[i2] = energies_i_raw[i]
        distances_f[i2] = distances_f_raw[i]

        start_points[i2] = np.array([point1x_raw[i], point1y_raw[i], point1z_raw[i]])
        end_points[i2] = np.array([point2x_raw[i], point2y_raw[i], point2z_raw[i]])

        start_end_points[i2*2] = start_points[i2]
        start_end_points[i2*2+1] = end_points[i2]
        i2 += 1

t2.task('post processing 2')
df = pd.DataFrame()
df['energies_f'] = energies_f
df['energies_i'] = energies_i
df['distances'] = distances_f
df['point1x'] = start_points[:, 0]
df['point1y'] = start_points[:, 1]
df['point1z'] = start_points[:, 2]
df['point2x'] = end_points[:, 0]
df['point2y'] = end_points[:, 1]
df['point2z'] = end_points[:, 2]

t2.task('write to HDF file')
df.to_hdf(config_file.hdf_folder+config_file.file_name_results, key=f'main', format='table')

s1 = f'({counter:.1f}) of {STATISTICS:.0e} ({counter/STATISTICS*100:.4})% detector hits'
# counter_u = ufloat(counter, np.sqrt(counter))
s2 = f'min(E_i) at detector = {min(energies_i)/1000:.1f} GeV'
print(f'{s1} | {s2}')

t2.stop(config_file.silent)
