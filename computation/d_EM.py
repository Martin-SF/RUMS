# %%
import py_library.stopwatch as stopwatch
t = stopwatch.stopwatch(title='d_EM', 
                        selfexecutiontime_micros=0, 
                        time_unit='s', 
                        return_results=True)

t.task('import')
import os
# os.chdir(os.path.dirname(__file__))
import numpy as np
# import matplotlib.pyplot as plt
# from tqdm import tqdm
import pandas as pd
# import proposal as pp
from importlib import reload
t.task('import2')

import py_library.my_plots_library as plib
import py_library.simulate_lib as slib
import config as cfg
t.task('import3')

# from distributed import Client, LocalCluster
from distributed import Client
from dask.distributed import performance_report
# import dask.bag as db
import dask.dataframe as dd
client = Client("localhost:8786")  # local client



# %%
# generating Muons with Ecomug into HDF
############################################################
############################################################
############################################################
t.task('load em lib')
import d_EM_lib as emo
t.task('dask upload file1')
# client.upload_file('config.py')
t.task('dask upload file2') 
client.upload_file('d_EM_lib.py')

# t.task('reload everything')
# reload(emo)
# reload(slib)
# reload(plib)
# reload(stopwatch)
# reload(cfg)

t.task('create zero hdf')
print(f'generating {cfg.file_name}')
chunksize = round((cfg.STATISTICS/cfg.N_tasks))+1

# local variable!!!
# workaround for a lot of tasks
tmphdf = cfg.hdf_folder+'tmp.hdf'
t.task('create zero hdf 1')
df = pd.DataFrame()
t.task('create zero hdf 2')
df['0'] = np.zeros(cfg.STATISTICS)
t.task('create zero hdf 3')
df.to_hdf(tmphdf, key=f'main', format='table')
t.task('pre processing 1')

with performance_report(filename="dask-report_EM.html"):
    df = dd.read_hdf(tmphdf, key='main', columns=['0'], chunksize=chunksize)
    bag = df.to_bag()
    # b = db.from_sequence(map(bool, arr), partition_size=chunksize)  # 1/2 slowdown
    bag = bag.map(emo.Ecomug_generate)
    t.task('pre processing 2')
    ddf = bag.to_dataframe()
    t.task('calculate muons with EcoMug', True)
    results = client.compute(ddf, pure=False).result()

os.remove(tmphdf)

t.task('post calculations')
results_array = np.array(results)

# muon_pos = np.zeros(shape=(cfg.STATISTICS, 3))
# muon_pos = np.array(list(results_array[:, 0]))
muon_x = np.array(results_array[:,0], dtype=float)
muon_y = np.array(results_array[:,1], dtype=float)
muon_z = np.array(results_array[:,2], dtype=float)
muon_p = np.array(results_array[:,3], dtype=float)
muon_theta = np.array(results_array[:, 4], dtype=float)
muon_phi = np.array(results_array[:, 5], dtype=float)
muon_charge = np.array(results_array[:, 6], dtype=np.int8)

muon_e = slib.calculate_energy_vectorized_GeV(muon_p)  # faster than for-loop


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

file_path = cfg.hdf_folder+cfg.file_name

if os.path.exists(file_path):
    os.remove(file_path)

df.to_hdf(file_path, key=f'main', format='table')

elapsed_time_total = t.stop(cfg.silent)['TOTAL']
# muonen_1e7_time = ( (elapsed_time_total/cfg.STATISTICS)*int(1e7))/(60*60)
# print(f'bei aktuellem xmom würden 1e7 muonen {muonen_1e7_time:2.1f} Stunden dauern')
print(f'Total time: {elapsed_time_total/(60):2.1f} min')