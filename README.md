# RICE

Study of siting optimization for recycling plants based on US geotemporal waste, enabled by PV ICE and RELOG open source tools. 


Installation
------------

1. Download the repository and install the python packages. You can do this by running

```
    pip install .
```

Alternatively, you can set up a virtual environment that includes all python packages required to run the repository files with the conda yaml file provided for convenient setup at setup/conda_environment.yml. Install the environment by running from the repository root directory:

```
    conda env create -f 'setup/conda_environment.yaml'
```

2. Install Julia, and then install RELOG

```
    using Pkg
    Pkg.add(name="RELOG", version="0.5")
```

More information on Relog installation is in [Relog's documentation](https://anl-ceeesa.github.io/RELOG/0.5/usage/)
