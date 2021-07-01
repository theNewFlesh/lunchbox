# Lunchbox
A library of various tools for common python tasks


See [documentation](https://theNewFlesh.github.io/lunchbox/) for details.

# Installation
### Python
`pip install lunchbox`

### Docker
1. Install
   [docker](https://docs.docker.com/v17.09/engine/installation)
2. Install
   [docker-machine](https://docs.docker.com/machine/install-machine)
   (if running on macOS or Windows)
3. `docker pull theNewFlesh/lunchbox:[version]`
4. `docker run --rm --name lunchbox-prod theNewFlesh/lunchbox:[version]`

### Docker For Developers
1. Install
   [docker](https://docs.docker.com/v17.09/engine/installation)
2. Install
   [docker-machine](https://docs.docker.com/machine/install-machine)
   (if running on macOS or Windows)
3. Ensure docker-machine has at least 4 GB of memory allocated to it.
4. `git clone git@github.com:theNewFlesh/lunchbox.git`
5. `cd lunchbox`
6. `chmod +x bin/lunchbox`
7. `bin/lunchbox start`

The service should take a few minutes to start up.

Run `bin/lunchbox --help` for more help on the command line tool.
