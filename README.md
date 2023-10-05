# RUMS Ruhrgebiet Myographie Simulation


Here are instructions to run the `computation.ipynb`

## preparations

### clone repo

`git clone https://github.com/Martin-SF/RUMS`

### Set up the conda environment
`conda create --name RUMS python=3.11 pip cmake`

`conda activate RUMS`

`pip install -r RUMS/requirements.txt`

### environment Variables (configure the paths for YOUR system)

(This is necessary so that the compiled Ecomug module and config.py can be found)

`conda env config vars set PYTHONPATH="$HOME/RUMS/computation/2EcoMug_pybind11/build:$PYTHONPATH"`

`conda env config vars set PYTHONPATH="$HOME/RUMS/computation:$PYTHONPATH"`

(This can be advantageous if Libpython is not found when PROPOSAL is imported or other programs fail weirdly (cmake for example) 

`conda env config vars set LD_LIBRARY_PATH="$HOME/.local/anaconda3/envs/RUMS/lib:$LD_LIBRARY_PATH"`

### Build EcoMug
`cd RUMS/computation/EcoMug_pybind11`

`mkdir build`

`cd build`

if this makes problems, maybe look into the env_3.10 environment requirement.txt. This environment is the only one that will compile Ecomug when using `phobos`...

`cmake .. -DCMAKE_BUILD_TYPE=Release`

`make`


## Done

Don't forget to restart the conda environment! (Als VSCode as whole if you use it (trust me...))

Now you should be able to run `computation/computation.ipynb`!
