<p>
    <a href="https://www.linkedin.com/in/alexandergbraun" rel="nofollow noreferrer">
        <img src="https://www.gomezaparicio.com/wp-content/uploads/2012/03/linkedin-logo-1-150x150.png"
             alt="linkedin" width="30px" height="30px"
        >
    </a>
    <a href="https://github.com/theNewFlesh" rel="nofollow noreferrer">
        <img src="https://tadeuzagallo.com/GithubPulse/assets/img/app-icon-github.png"
             alt="github" width="30px" height="30px"
        >
    </a>
    <a href="https://pypi.org/user/the-new-flesh" rel="nofollow noreferrer">
        <img src="https://cdn.iconscout.com/icon/free/png-256/python-2-226051.png"
             alt="pypi" width="30px" height="30px"
        >
    </a>
    <a href="http://vimeo.com/user3965452" rel="nofollow noreferrer">
        <img src="https://cdn1.iconfinder.com/data/icons/somacro___dpi_social_media_icons_by_vervex-dfjq/500/vimeo.png"
             alt="vimeo" width="30px" height="30px"
        >
    </a>
    <a href="http://www.alexgbraun.com" rel="nofollow noreferrer">
        <img src="https://i.ibb.co/fvyMkpM/logo.png"
             alt="alexgbraun" width="30px" height="30px"
        >
    </a>
</p>


# Introduction
Lunchbox is a library of various tools for common python tasks.

See [documentation](https://theNewFlesh.github.io/lunchbox/) for details.

# Installation
### Python
`pip install lunchbox`

### Docker
1. Install [docker-desktop](https://docs.docker.com/desktop/)
2. `docker pull thenewflesh/lunchbox:latest`

### Docker For Developers
1. Install [docker-desktop](https://docs.docker.com/desktop/)
2. Ensure docker-desktop has at least 4 GB of memory allocated to it.
4. `git clone git@github.com:theNewFlesh/lunchbox.git`
5. `cd lunchbox`
6. `chmod +x bin/lunchbox`
7. `bin/lunchbox start`

The service should take a few minutes to start up.

Run `bin/lunchbox --help` for more help on the command line tool.

# Production CLI

Lunchbox comes with a command line interface defined in command.py.

Its usage pattern is: `lunchbox COMMAND [ARGS] [-h --help]`

### Commands
| Command         | Description                                                              | Args                  |
| --------------- | -------------------------------------------------------------------------| --------------------- |
| slack           | Posts a slack message to a given channel                                 | url, channel, message |
| bash-completion | Prints BASH completion code to be written to a _lunchbox completion file |                       |
| zsh-completion  | Prints ZSH completion code to be written to a _lunchbox completion file  |                       |

# Development CLI
bin/lunchbox is a command line interface (defined in cli.py) that works with
any version of python 2.7 and above, as it has no dependencies.

Its usage pattern is: `bin/lunchbox COMMAND [-a --args]=ARGS [-h --help] [--dryrun]`

### Commands

| Command              | Description                                                         |
| -------------------- | ------------------------------------------------------------------- |
| build-package        | Build production version of repo for publishing                     |
| build-prod           | Publish pip package of repo to PyPi                                 |
| build-publish        | Run production tests first then publish pip package of repo to PyPi |
| build-test           | Build test version of repo for prod testing                         |
| docker-build         | Build image of lunchbox                                             |
| docker-build-prod    | Build production image of lunchbox                                  |
| docker-container     | Display the Docker container id of lunchbox                         |
| docker-coverage      | Generate coverage report for lunchbox                               |
| docker-destroy       | Shutdown lunchbox container and destroy its image                   |
| docker-destroy-prod  | Shutdown lunchbox production container and destroy its image        |
| docker-image         | Display the Docker image id of lunchbox                             |
| docker-prod          | Start lunchbox production container                                 |
| docker-push          | Push lunchbox production image to Dockerhub                         |
| docker-remove        | Remove lunchbox Docker image                                        |
| docker-restart       | Restart lunchbox container                                          |
| docker-start         | Start lunchbox container                                            |
| docker-stop          | Stop lunchbox container                                             |
| docs                 | Generate sphinx documentation                                       |
| docs-architecture    | Generate architecture.svg diagram from all import statements        |
| docs-full            | Generate documentation, coverage report, diagram and code           |
| docs-metrics         | Generate code metrics report, plots and tables                      |
| library-add          | Add a given package to a given dependency group                     |
| library-graph-dev    | Graph dependencies in dev environment                               |
| library-graph-prod   | Graph dependencies in prod environment                              |
| library-install-dev  | Install all dependencies into dev environment                       |
| library-install-prod | Install all dependencies into prod environment                      |
| library-list-dev     | List packages in dev environment                                    |
| library-list-prod    | List packages in prod environment                                   |
| library-lock-dev     | Resolve dev.lock file                                               |
| library-lock-prod    | Resolve prod.lock file                                              |
| library-remove       | Remove a given package from a given dependency group                |
| library-search       | Search for pip packages                                             |
| library-sync-dev     | Sync dev environment with packages listed in dev.lock               |
| library-sync-prod    | Sync prod environment with packages listed in prod.lock             |
| library-update       | Update dev dependencies                                             |
| session-lab          | Run jupyter lab server                                              |
| session-python       | Run python session with dev dependencies                            |
| state                | State of lunchbox                                                   |
| test-coverage        | Generate test coverage report                                       |
| test-dev             | Run all tests                                                       |
| test-fast            | Test all code excepts tests marked with SKIP_SLOWS_TESTS decorator  |
| test-lint            | Run linting and type checking                                       |
| test-prod            | Run tests across all support python versions                        |
| version              | Full resolution of repo: dependencies, linting, tests, docs, etc    |
| version-bump-major   | Bump pyproject major version                                        |
| version-bump-minor   | Bump pyproject minor version                                        |
| version-bump-patch   | Bump pyproject patch version                                        |
| zsh                  | Run ZSH session inside lunchbox container                           |
| zsh-complete         | Generate oh-my-zsh completions                                      |
| zsh-root             | Run ZSH session as root inside lunchbox container                   |

### Flags

| Short | Long      | Description                                          |
| ----- | --------- | ---------------------------------------------------- |
| -a    | --args    | Additional arguments, this can generally be ignored  |
| -h    | --help    | Prints command help message to stdout                |
|       | --dryrun  | Prints command that would otherwise be run to stdout |
