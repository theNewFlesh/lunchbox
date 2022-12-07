Introduction
============

Lunchbox is a library of various tools for common python tasks.

See `documentation <https://theNewFlesh.github.io/lunchbox/>`__ for
details.

Installation
============

Python
~~~~~~

``pip install lunchbox``

Docker
~~~~~~

1. Install `docker-desktop <https://docs.docker.com/desktop/>`__
2. ``docker pull thenewflesh/lunchbox:latest``

Docker For Developers
~~~~~~~~~~~~~~~~~~~~~

1. Install `docker-desktop <https://docs.docker.com/desktop/>`__
2. Ensure docker-desktop has at least 4 GB of memory allocated to it.
3. ``git clone git@github.com:theNewFlesh/lunchbox.git``
4. ``cd lunchbox``
5. ``chmod +x bin/lunchbox``
6. ``bin/lunchbox start``

The service should take a few minutes to start up.

Run ``bin/lunchbox --help`` for more help on the command line tool.

Production CLI
==============

Lunchbox comes with a command line interface defined in command.py.

Its usage pattern is: ``lunchbox COMMAND [ARGS] [-h --help]``

Commands
~~~~~~~~

+--------+-----------------------------------------------+------------+
| C      | Description                                   | Args       |
| ommand |                                               |            |
+========+===============================================+============+
| slack  | Posts a slack message to a given channel      | url,       |
|        |                                               | channel,   |
|        |                                               | message    |
+--------+-----------------------------------------------+------------+
| bas    | Prints BASH completion code to be written to  |            |
| h-comp | a \_lunchbox completion file                  |            |
| letion |                                               |            |
+--------+-----------------------------------------------+------------+
| zs     | Prints ZSH completion code to be written to a |            |
| h-comp | \_lunchbox completion file                    |            |
| letion |                                               |            |
+--------+-----------------------------------------------+------------+

Development CLI
===============

bin/lunchbox is a command line interface (defined in cli.py) that works
with any version of python 2.7 and above, as it has no dependencies.

Its usage pattern is:
``bin/lunchbox COMMAND [-a --args]=ARGS [-h --help] [--dryrun]``

.. _commands-1:

Commands
~~~~~~~~

+---------------+------------------------------------------------------+
| Command       | Description                                          |
+===============+======================================================+
| build-package | Build production version of repo for publishing      |
+---------------+------------------------------------------------------+
| build-prod    | Publish pip package of repo to PyPi                  |
+---------------+------------------------------------------------------+
| build-publish | Run production tests first then publish pip package  |
|               | of repo to PyPi                                      |
+---------------+------------------------------------------------------+
| build-test    | Build test version of repo for prod testing          |
+---------------+------------------------------------------------------+
| docker-build  | Build image of lunchbox                              |
+---------------+------------------------------------------------------+
| dock          | Build production image of lunchbox                   |
| er-build-prod |                                                      |
+---------------+------------------------------------------------------+
| doc           | Display the Docker container id of lunchbox          |
| ker-container |                                                      |
+---------------+------------------------------------------------------+
| do            | Generate coverage report for lunchbox                |
| cker-coverage |                                                      |
+---------------+------------------------------------------------------+
| d             | Shutdown lunchbox container and destroy its image    |
| ocker-destroy |                                                      |
+---------------+------------------------------------------------------+
| docker        | Shutdown lunchbox production container and destroy   |
| -destroy-prod | its image                                            |
+---------------+------------------------------------------------------+
| docker-image  | Display the Docker image id of lunchbox              |
+---------------+------------------------------------------------------+
| docker-prod   | Start lunchbox production container                  |
+---------------+------------------------------------------------------+
| docker-push   | Push lunchbox production image to Dockerhub          |
+---------------+------------------------------------------------------+
| docker-remove | Remove lunchbox Docker image                         |
+---------------+------------------------------------------------------+
| d             | Restart lunchbox container                           |
| ocker-restart |                                                      |
+---------------+------------------------------------------------------+
| docker-start  | Start lunchbox container                             |
+---------------+------------------------------------------------------+
| docker-stop   | Stop lunchbox container                              |
+---------------+------------------------------------------------------+
| docs          | Generate sphinx documentation                        |
+---------------+------------------------------------------------------+
| docs          | Generate architecture.svg diagram from all import    |
| -architecture | statements                                           |
+---------------+------------------------------------------------------+
| docs-full     | Generate documentation, coverage report, diagram and |
|               | code                                                 |
+---------------+------------------------------------------------------+
| docs-metrics  | Generate code metrics report, plots and tables       |
+---------------+------------------------------------------------------+
| library-add   | Add a given package to a given dependency group      |
+---------------+------------------------------------------------------+
| libr          | Graph dependencies in dev environment                |
| ary-graph-dev |                                                      |
+---------------+------------------------------------------------------+
| libra         | Graph dependencies in prod environment               |
| ry-graph-prod |                                                      |
+---------------+------------------------------------------------------+
| librar        | Install all dependencies into dev environment        |
| y-install-dev |                                                      |
+---------------+------------------------------------------------------+
| library       | Install all dependencies into prod environment       |
| -install-prod |                                                      |
+---------------+------------------------------------------------------+
| lib           | List packages in dev environment                     |
| rary-list-dev |                                                      |
+---------------+------------------------------------------------------+
| libr          | List packages in prod environment                    |
| ary-list-prod |                                                      |
+---------------+------------------------------------------------------+
| lib           | Resolve dev.lock file                                |
| rary-lock-dev |                                                      |
+---------------+------------------------------------------------------+
| libr          | Resolve prod.lock file                               |
| ary-lock-prod |                                                      |
+---------------+------------------------------------------------------+
| l             | Remove a given package from a given dependency group |
| ibrary-remove |                                                      |
+---------------+------------------------------------------------------+
| l             | Search for pip packages                              |
| ibrary-search |                                                      |
+---------------+------------------------------------------------------+
| lib           | Sync dev environment with packages listed in         |
| rary-sync-dev | dev.lock                                             |
+---------------+------------------------------------------------------+
| libr          | Sync prod environment with packages listed in        |
| ary-sync-prod | prod.lock                                            |
+---------------+------------------------------------------------------+
| l             | Update dev dependencies                              |
| ibrary-update |                                                      |
+---------------+------------------------------------------------------+
| session-lab   | Run jupyter lab server                               |
+---------------+------------------------------------------------------+
| s             | Run python session with dev dependencies             |
| ession-python |                                                      |
+---------------+------------------------------------------------------+
| state         | State of lunchbox                                    |
+---------------+------------------------------------------------------+
| test-coverage | Generate test coverage report                        |
+---------------+------------------------------------------------------+
| test-dev      | Run all tests                                        |
+---------------+------------------------------------------------------+
| test-fast     | Test all code excepts tests marked with              |
|               | SKIP_SLOWS_TESTS decorator                           |
+---------------+------------------------------------------------------+
| test-lint     | Run linting and type checking                        |
+---------------+------------------------------------------------------+
| test-prod     | Run tests across all support python versions         |
+---------------+------------------------------------------------------+
| version       | Full resolution of repo: dependencies, linting,      |
|               | tests, docs, etc                                     |
+---------------+------------------------------------------------------+
| versi         | Bump pyproject major version                         |
| on-bump-major |                                                      |
+---------------+------------------------------------------------------+
| versi         | Bump pyproject minor version                         |
| on-bump-minor |                                                      |
+---------------+------------------------------------------------------+
| versi         | Bump pyproject patch version                         |
| on-bump-patch |                                                      |
+---------------+------------------------------------------------------+
| zsh           | Run ZSH session inside lunchbox container            |
+---------------+------------------------------------------------------+
| zsh-complete  | Generate oh-my-zsh completions                       |
+---------------+------------------------------------------------------+
| zsh-root      | Run ZSH session as root inside lunchbox container    |
+---------------+------------------------------------------------------+

Flags
~~~~~

===== ======= ====================================================
Short Long    Description
===== ======= ====================================================
-a    –args   Additional arguments, this can generally be ignored
-h    –help   Prints command help message to stdout
\     –dryrun Prints command that would otherwise be run to stdout
===== ======= ====================================================
