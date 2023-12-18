# RUMS RUhrgebiet Myographie Simulation

All simulations are performed in `computation/computation.ipynb`

## Setup

### Clone repo

`git clone https://github.com/Martin-SF/RUMS`

### Set up the conda environment
`conda create --name RUMS python=3.11 pip cmake`

`conda activate RUMS`

`pip install -r RUMS/requirements.txt`

### Environment variables (configure the paths for YOUR system)

(This is necessary so that the compiled Ecomug module and config.py can be found)

`conda env config vars set PYTHONPATH="$HOME/RUMS/computation/EcoMug_pybind11/build:$PYTHONPATH"`

`conda env config vars set PYTHONPATH="$HOME/RUMS/computation:$PYTHONPATH"`

(This can be advantageous if `libpython` is not found (for example PROPOSAL)

`conda env config vars set LD_LIBRARY_PATH="$HOME/.local/anaconda3/envs/RUMS/lib:$LD_LIBRARY_PATH"`

### Build EcoMug
`cd RUMS/computation/EcoMug_pybind11`

`mkdir build`

`cd build`

`cmake .. -DCMAKE_BUILD_TYPE=Release`

`make`

## Done

Don't forget to restart the conda environment! (also VSCode as whole is a good idea)

Now you can continue in `computation/computation.ipynb`.


# Tips

* dont forget to change the `hdf_folder` for your system `pp_tables_path` 

* use subfolder parameter for marking of individual tests

* You can get more performance insights on the dask dashboard on localhost:8787

* update packages: `conda update --all` and `pip install -U -r requirements.txt`