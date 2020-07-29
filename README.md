# Lunchbox
A library of various tools for common python tasks

**[Documentation](https://thenewflesh.github.io/lunchbox/)**

On the documentation main page, under the *Architecture* section, is a
dynamically generated dependency graph of lunchbox's current architecture.
It is generated using the RepoETL class.

If you look under the *Metrics* section you will find Radon code metric plots
and data of the lunchbox source code.

# Installation
`pip install lunchbox`

# For Developers
## Installation
1. Install [docker](https://docs.docker.com/v17.09/engine/installation)
2. Install [docker-machine](https://docs.docker.com/machine/install-machine)
   (if running on macOS or Windows)
3. Ensure docker-machine has at least 4 GB of memory allocated to it.
4. `cd lunchbox`
5. `chmod +x bin/lunchbox`
6. `bin/lunchbox start`

The service should take a few minutes to start up.

Run `bin/lunchbox --help` for more help on the command line tool.

## Conda Environment Creation
Running a conda environment is not recommended.

However, if you would still like to build one, do the following:
1. `conda create -y -n lunchbox-env python==3.7`
2. `source activate lunchbox-env`
3. `pip install -r docker/dev_requirements.txt`
4. `pip install -r docker/prod_requirements.txt`
