# EXPORTS-----------------------------------------------------------------------
export HOME="/home/ubuntu"
export REPO="lunchbox"
export REPO_DIR="$HOME/$REPO"
export PATH=":$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.local/lib"
export PYTHONPATH="$REPO_DIR/python:$HOME/.local/lib"
export BUILD_DIR="$HOME/build"
export CONFIG_DIR="$REPO_DIR/docker/config"
export PDM_DIR="$HOME/pdm"
export SCRIPT_DIR="$REPO_DIR/docker/scripts"
export PROCS=`python3 -c 'import os; print(os.cpu_count())'`
export MAX_PYTHON_VERSION="3.10"
export MIN_PYTHON_VERSION="3.7"
export X_TOOLS_PATH="$SCRIPT_DIR/x-tools.sh"
unalias cp  # "cp -i" alias asks you if you want to clobber files

# GENERATE-FUNCTIONS------------------------------------------------------------
_x_gen_pyproject () {
    # Generates pyproject.toml content given a mode
    # args: mode (dev, test or prod)
    if [[ $1 == "dev" ]]; then
        python3 $SCRIPT_DIR/toml_gen.py $CONFIG_DIR/pyproject.toml \
            --replace "project.name,lunchbox-dev";

    elif [[ $1 == "test" ]]; then
        python3 $SCRIPT_DIR/toml_gen.py $CONFIG_DIR/pyproject.toml \
            --replace "project.requires-python,>=$MIN_PYTHON_VERSION" \
            --delete "tool.pdm.dev-dependencies.lab" \
            --delete "tool.pdm.dev-dependencies.dev";

    elif [[ $1 == "prod" ]]; then
        python3 $SCRIPT_DIR/toml_gen.py $CONFIG_DIR/pyproject.toml \
            --replace "project.requires-python,>=$MIN_PYTHON_VERSION" \
            --delete "tool.pdm.dev-dependencies" \
            --delete "tool.mypy" \
            --delete "tool.pdm" \
            --delete "tool.pytest" \
            --delete "tool.tox";
    fi;
}

_x_gen_pdm_files () {
    # Generate pyproject.tom, .pdm.toml and pdm.lock files
    # args: mode, python version

    # pyproject.toml
    _x_gen_pyproject $1 > $PDM_DIR/pyproject.toml;

    # pdm.lock
    rm -f $PDM_DIR/pdm.lock;
    cp $CONFIG_DIR/$1.lock $PDM_DIR/pdm.lock;

    # get python path
    local pypath=`_x_get_env_python $1 $2`;

    # .pdm.toml
    python3 $SCRIPT_DIR/toml_gen.py $CONFIG_DIR/pdm.toml \
        --replace "venv.prompt,$1-{python_version}" \
        --replace "python.path,$pypath" \
        > $PDM_DIR/.pdm.toml;
}

# ENV-FUNCTIONS-----------------------------------------------------------------
_x_get_env_path () {
    # gets path of given environment
    # args: environment name
    cd $PDM_DIR;
    pdm venv list | grep $1 | awk '{print $3}';
}

_x_env_exists () {
    # determines if given env exists
    # args: environment name
    cd $PDM_DIR;
    if [[ `pdm venv list | grep $1` ]]; then
        echo "true";
    else
        echo "false";
    fi;
}

_x_get_env_python () {
    # gets python interpreter path of given environment
    # args: mode, python version
    local env=`_x_get_env_path $1-$2`;
    if [[ $env ]]; then
        echo $env;
    else
        echo /usr/bin/python$2;
    fi;
}

_x_env_create () {
    # Create a virtual env given a mode and python version
    # args: mode, python_version
    cd $PDM_DIR;
    _x_gen_pdm_files $1 $2;
    pdm venv create -n $1-$2;
}

_x_env_activate () {
    # Activate a virtual env given a mode and python version
    # args: mode, python_version
    cd $PDM_DIR;
    _x_gen_pdm_files $1 $2;
    . `pdm venv activate $1-$2 | awk '{print $2}'`;
}

_x_env_lock () {
    # Resolve dependencies listed in pyrproject.toml into a pdm.lock file
    # args: mode, python_version
    cd $PDM_DIR;
    _x_env_activate $1 $2 && \
    pdm lock -v && \
    cat $PDM_DIR/pdm.lock > $CONFIG_DIR/$1.lock;
}

_x_env_sync () {
    # Install dependencies from a pdm.lock into a virtual env specified by a
    # given mode and python version
    # args: mode, python_version
    cd $PDM_DIR;
    _x_env_activate $1 $2 && \
    pdm sync --no-self --dev --clean -v && \
    deactivate;
}

x_env_activate_dev () {
    # Activates dev environment
    _x_env_activate dev $MAX_PYTHON_VERSION;
}

x_env_init () {
    # Create a virtual env with dependencies given a mode and python version
    # args: mode, python_version
    cd $PDM_DIR;
    _x_env_create $1 $2;
    _x_env_sync $1 $2;
}

# BUILD-FUNCTIONS---------------------------------------------------------------
_x_build () {
    # Build production version of repo for publishing
    # args: type (test or prod)
    x_env_activate_dev;
    rm -rf $BUILD_DIR;
    python3 \
        $SCRIPT_DIR/rolling_pin_command.py \
        $CONFIG_DIR/build.yaml \
        --groups base,$1;
    _x_gen_pyproject $1 > $BUILD_DIR/repo/pyproject.toml;
}

x_build_package () {
    # Generate pip package of repo in $HOME/build/repo
    x_env_activate_dev;
    x_build_prod;
    cd $BUILD_DIR/repo;
    echo "${CYAN}BUILDING PIP PACKAGE${CLEAR}\n";
    pdm build --dest $BUILD_DIR/dist -v;
    rm -rf $BUILD_DIR/repo/build;
}

x_build_prod () {
    # Build production version of repo for publishing
    echo "${CYAN}BUILDING PROD REPO${CLEAR}\n";
    _x_build prod;
}

x_build_publish () {
    # Publish pip package of repo to PyPi
    # args: user, password, comment
    x_test_lint;
    cd $REPO_DIR;
    x_test_prod;
    cd $REPO_DIR;
    x_build_package;
    echo "${CYAN}PUBLISHING PIP PACKAGE TO PYPI${CLEAR}\n";
    cd $BUILD_DIR/repo;
    pdm publish \
        --no-build \
        --username "$1" \
        --password "$2" \
        --comment "$3" \
        --verbose;
}

x_build_test () {
    # Build test version of repo for tox testing
    echo "${CYAN}BUILDING TEST REPO${CLEAR}\n";
    _x_build test;
}

# DOCS-FUNCTIONS----------------------------------------------------------------
x_docs () {
    # Generate sphinx documentation
    x_env_activate_dev;
    cd $REPO_DIR;
    echo "${CYAN}GENERATING DOCS${CLEAR}\n";
    mkdir -p docs;
    pandoc README.md -o sphinx/intro.rst;
    sphinx-build sphinx docs;
    cp -f sphinx/style.css docs/_static/style.css;
    touch docs/.nojekyll;
    mkdir -p docs/resources;
}

x_docs_architecture () {
    # Generate architecture.svg diagram from all import statements
    echo "${CYAN}GENERATING ARCHITECTURE DIAGRAM${CLEAR}\n";
    x_env_activate_dev;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_architecture( \
    '$REPO_DIR/python', \
    '$REPO_DIR/docs/architecture.svg', \
    exclude_regex='test|mock', \
    orient='lr', \
)";
}

x_docs_full () {
    # Generate documentation, coverage report, architecture diagram and code
    # metrics
    x_docs && x_docs_metrics && x_docs_architecture && x_test_coverage;
}

x_docs_metrics () {
    # Generate code metrics report, plots and tables
    echo "${CYAN}GENERATING METRICS${CLEAR}\n";
    x_env_activate_dev;
    cd $REPO_DIR;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_plots_and_tables('python', 'docs/plots.html', 'docs')"
}

# LIBRARY-FUNCTIONS-------------------------------------------------------------
x_library_add () {
    # Add a given package to a given dependency group
    # args: package, group
    echo "${CYAN}ADDING PACKAGE TO DEV DEPENDENCIES${CLEAR}\n";
    _x_from_dev_path;
    cd $DEV_TARGET;
    if [[ $2 == 'none' ]]; then
        pdm add $1 -v;
    else
        pdm add -dG $2 $1 -v;
    fi;
    _x_to_dev_path;
}

x_library_graph_dev () {
    # Graph dependencies in dev environment
    _x_from_dev_path;
    echo "${CYAN}DEV DEPENDENCY GRAPH${CLEAR}\n";
    cd $DEV_TARGET;
    pdm list --graph;
}

x_library_graph_prod () {
    # Graph dependencies in prod environment
    _x_from_prod_path;
    echo "${CYAN}PROD DEPENDENCY GRAPH${CLEAR}\n";
    cd $PROD_TARGET;
    pdm list --graph;
}

x_library_install_dev () {
    # Install all dependencies of dev/pyproject.toml into $HOME/dev
    echo "${CYAN}INSTALL DEV${CLEAR}\n";
    _x_workflow_dev "pdm install --no-self --dev -v";
}

x_library_install_prod () {
    # Install all dependencies of prod/pyproject.toml into $HOME/prod
    echo "${CYAN}INSTALL PROD${CLEAR}\n";
    _x_gen_prod;
    cd $PROD_TARGET;
    _x_from_prod_path;
    pdm install --no-self --dev -v;
    _x_to_prod_path;
}

x_library_list_dev () {
    # List packages in dev environment
    _x_from_dev_path;
    echo "${CYAN}DEV DEPENDENCIES${CLEAR}\n";
    cd $DEV_TARGET;
    pdm list;
}

x_library_list_prod () {
    # List packages in prod environment
    _x_from_prod_path;
    echo "${CYAN}PROD DEPENDENCIES${CLEAR}\n";
    cd $PROD_TARGET;
    pdm list;
}

x_library_lock () {
    # Update $HOME/dev/pdm.lock file
    echo "${CYAN}DEV DEPENDENCY LOCK${CLEAR}\n";
    _x_workflow_dev "pdm lock -v";
}

x_library_remove () {
    # Remove a given package from a given dependency group
    # args: package, group
    echo "${CYAN}REMOVING PACKAGE FROM DEV DEPENDENCIES${CLEAR}\n";
    _x_from_dev_path;
    cd $DEV_TARGET;
    if [[ $2 == 'none' ]]; then
        pdm remove $1 -v;
    else
        pdm remove -dG $2 $1 -v;
    fi;
    _x_to_dev_path;
}

x_library_search () {
    # Search for pip packages
    # args: package name
    pdm search $1;
}

x_library_sync () {
    # Sync dev dependencies
    echo "${CYAN}SYNCING DEV DEPENDENCIES${CLEAR}\n";
    _x_workflow_dev "pdm sync --no-self --dev -v";
}

x_library_update () {
    # Update dev dependencies
    echo "${CYAN}UPDATING DEV DEPENDENCIES${CLEAR}\n";
    _x_workflow_dev "pdm update --no-self --dev -v";
}

# SESSION-FUNCTIONS-------------------------------------------------------------
x_session_app () {
    # Run lunchbox app
    echo "${CYAN}APP${CLEAR}\n";
    _x_link_dev;
    python3.10 python/$REPO/server/app.py;
}

x_session_lab () {
    # Run jupyter lab server
    echo "${CYAN}JUPYTER LAB${CLEAR}\n";
    _x_link_dev;
    jupyter lab --allow-root --ip=0.0.0.0 --no-browser;
}

x_session_python () {
    # Run python session with dev dependencies
    _x_link_dev;
    python3.10;
}

# TEST-FUNCTIONS----------------------------------------------------------------
x_test_coverage () {
    # Generate test coverage report
    echo "${CYAN}GENERATING TEST COVERAGE REPORT${CLEAR}\n";
    _x_link_dev;
    cd $REPO_DIR;
    mkdir -p docs;
    pytest \
        -c docker/dev/pyproject.toml \
        --numprocesses $PROCS \
        --cov=python \
        --cov-config=docker/dev/pyproject.toml \
        --cov-report=html:docs/htmlcov \
        python;
}

x_test_dev () {
    # Run all tests
    echo "${CYAN}TESTING DEV${CLEAR}\n";
    _x_link_dev;
    cd $REPO_DIR;
    pytest -c docker/dev/pyproject.toml --numprocesses $PROCS python;
}

x_test_fast () {
    # Test all code excepts tests marked with SKIP_SLOWS_TESTS decorator
    echo "${CYAN}FAST TESTING DEV${CLEAR}\n";
    _x_link_dev;
    cd $REPO_DIR;
    SKIP_SLOW_TESTS=true \
    pytest -c docker/dev/pyproject.toml --numprocesses $PROCS python;
}

x_test_lint () {
    # Run linting and type checking
    _x_link_dev;
    cd $REPO_DIR;
    echo "${CYAN}LINTING${CLEAR}\n";
    flake8 python --config docker/config/flake8.ini;
    echo "${CYAN}TYPE CHECKING${CLEAR}\n";
    mypy python --config-file docker/dev/pyproject.toml;
}

x_test_prod () {
    # Run tests across all support python versions
    _x_gen_prod;
    x_build_test;
    _x_link_prod;
    echo "${CYAN}TESTING PROD${CLEAR}\n";
    cd $BUILD_DIR/repo;
    tox --parallel -v;
}

# VERSION-FUNCTIONS-------------------------------------------------------------
x_version () {
    # Full resolution of repo: dependencies, linting, tests, docs, etc
    _x_link_dev;
    x_test_lint;
    x_library_install_dev;
    x_docs_full;
}

x_version_bump_major () {
    # Bump repo's major version
    echo "${CYAN}BUMPING MAJOR VERSION${CLEAR}\n";
    _x_workflow_dev "pdm bump major";
}

x_version_bump_minor () {
    # Bump repo's minor version
    echo "${CYAN}BUMPING MINOR VERSION${CLEAR}\n";
    _x_workflow_dev "pdm bump minor";
}

x_version_bump_patch () {
    # Bump repo's patch version
    echo "${CYAN}BUMPING PATCH VERSION${CLEAR}\n";
    _x_workflow_dev "pdm bump patch";
}
