# EXPORTS-----------------------------------------------------------------------
export PATH=:/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/bin
export PYTHONPATH=/home/ubuntu/lunchbox/python:/home/ubuntu/.local/share/pdm/venv/lib/python3.10/site-packages/pdm/pep582:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/lib
export REPO="lunchbox"
export REPO_PATH="/home/ubuntu/$REPO"
export BUILD_PATH="/home/ubuntu/build"
export GEN_PATH="$REPO_PATH/docker/scripts/toml_gen.py"
export PROJ_PATH="$REPO_PATH/docker/pyproject.toml"
export DEV_SOURCE="$REPO_PATH/docker/dev"
export DEV_TARGET="/home/ubuntu/dev"
export PROD_SOURCE="$REPO_PATH/docker/prod"
export PROD_TARGET="/home/ubuntu/prod"
export PROCS=`python3 -c 'import os; print(os.cpu_count())'`
export X_TOOLS_PATH="$REPO_PATH/docker/scripts/x-tools.sh"

# HELPER-FUNCTIONS--------------------------------------------------------------
_x_link () {
    # Link given __pypackages__ directory to /home/ubuntu/__pypackages__
    # args: pypackages directory
    rm -f /home/ubuntu/__pypackages__;
    ln -s $1 /home/ubuntu/__pypackages__;
}

_x_link_dev () {
    # Link /home/ubuntu/dev/__pypackages__ to /home/ubuntu/__pypackages__
    _x_link $DEV_TARGET/__pypackages__;
}

_x_link_prod () {
    # Link /home/ubuntu/prod/__pypackages__ to /home/ubuntu/__pypackages__
    _x_link $PROD_TARGET/__pypackages__;
}

_x_dir_copy () {
    # copy all contents of source into target, skipping __pypackages__ directory
    # args: source, target
    ls -pA $1 | grep -v '/' \
    | parallel "cp --force $1/{} $2/{}";
}

_x_from_dev_path () {
    # Copy lunchbox/docker/dev to /home/ubuntu/dev
    _x_dir_copy $DEV_SOURCE $DEV_TARGET;
}

_x_from_prod_path () {
    # Copy lunchbox/docker/prod to /home/ubuntu/prod
    _x_dir_copy $PROD_SOURCE $PROD_TARGET;
}

_x_to_dev_path () {
    # Copy /home/ubuntu/dev to lunchbox/docker/dev
    _x_dir_copy $DEV_TARGET $DEV_SOURCE;
}

_x_to_prod_path () {
    # Copy /home/ubuntu/prod to lunchbox/docker/prod
    _x_dir_copy $PROD_TARGET $PROD_SOURCE;
}

_x_build () {
    # Build production version of repo for publishing
    # args: type (test or prod)
    _x_link_dev;
    cd $REPO_PATH;
    rm -rf $BUILD_PATH;
    python3 docker/scripts/rolling_pin_command.py \
        docker/config/build.yaml \
        --groups base,$1;
}

_x_workflow_dev () {
    # Copies docker/dev to ~/dev, run a given command, and copies ~/dev back to
    # docker/dev
    # args: command string
    local CWD=`pwd`;
    _x_link_dev;
    _x_dir_copy $DEV_SOURCE $DEV_TARGET;
    cd $DEV_TARGET;
    eval "$1";
    _x_dir_copy $DEV_TARGET $DEV_SOURCE;
    cd $CWD;
}

_x_workflow_prod () {
    # Copies docker/prod to ~/prod, run a given command, and copies ~/prod back
    # to docker/prod
    # args: command string
    local CWD=`pwd`;
    _x_link_dev;
    _x_generate_prod;
    _x_dir_copy $PROD_SOURCE $PROD_TARGET;
    cd $PROD_TARGET;
    eval "$1";
    _x_dir_copy $PROD_TARGET $PROD_SOURCE;
    cd $CWD;
}

_x_generate_dev () {
    # Generate ~/dev/pyproject.toml from docker/pyproject.toml.j2
    _x_link_dev;
    jinja docker/pyproject.toml.j2 --define mode prod \
    > $PROD_SOURCE/pyproject.toml;
    _x_from_prod_path;
}

_x_generate_prod () {
    # Generate ~/prod/pyproject.toml from docker/pyproject.toml.j2
    _x_link_dev;
    python3 $GEN_PATH $PROJ_PATH \
        --replace 'project.requires-python,>=3.7' \
        --delete 'tool.pdm.dev-dependencies.lab' \
        --delete 'tool.pdm.dev-dependencies.dev' \
    > $PROD_SOURCE/pyproject.toml;
    python3 $GEN_PATH $PDM_PATH \
        --replace 'venv.prompt,prod-{python_version}' \
        --replace "python.path,$path";
    > $PROD_SOURCE/.pdm.toml;
    cp --force $REPO_PATH/docker/prod.lock /home/ubuntu/pdm/pdm.lock;
    _x_from_prod_path;
}

# ENV-FUNCTIONS-----------------------------------------------------------------
x_env_setup () {
    # Configure pdm directory according to given a mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    cp --force $1.lock pdm.lock;
    jinja pyproject.toml.j2 --define mode $1 > pyproject.toml;
    jinja pdm.toml.j2 \
        --define mode $1 \
        --define python_path /usr/bin/python$2 \
        > .pdm.toml;
}

x_env_create () {
    # Create a virtual env given a mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    x_env_setup $1 $2;
    pdm venv create -n $1-$2;
}

x_env_activate () {
    # Activate a virtual env given a mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    local temp=`pdm venv list | grep $1-$2 | awk '{print $3}'`/bin/python;
    jinja pdm.toml.j2 \
        --define mode $1 \
        --define python_path $temp \
        > .pdm.toml;
    . `pdm venv activate $1-$2 | awk '{print $2}'`;
}

x_env_install () {
    # Resolve and install dependencies into a virtual env specified by a given
    # mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    x_env_activate $1 $2;
    pdm install --no-self --dev -v;
    deactivate;
}

x_env_lock () {
    # Resolve dependencies listed in pyrproject.toml into a pdm.lock file
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    pdm lock --no-self --dev -v;
}

x_env_sync () {
    # Install dependencies from a pdm.lock into a virtual env specified by a
    # given mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    x_env_activate $1 $2;
    pdm sync --no-self --dev --clean -v;
    deactivate;
}

x_env_init () {
    # Create a virtual env with dependencies given a mode and python version
    # args: mode, python_version
    cd /home/ubuntu/pdm;
    x_env_create $1 $2;
    x_env_sync $1 $2;
}

# TASK-FUNCTIONS----------------------------------------------------------------
x_build_pip_package () {
    # Generate pip package of repo in /home/ubuntu/build/repo
    x_library_install_prod;
    x_build_prod;
    cd $BUILD_PATH/repo;
    echo "${CYAN}BUILDING PIP PACKAGE${CLEAR}\n";
    pdm build -v;
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
    cd $REPO_PATH;
    x_test_prod;
    cd $REPO_PATH;
    x_build_pip_package;
    echo "${CYAN}PUBLISHING PIP PACKAGE TO PYPI${CLEAR}\n";
    cd $BUILD_PATH/repo;
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

x_docs () {
    # Generate sphinx documentation
    echo "${CYAN}GENERATING DOCS${CLEAR}\n";
    _x_link_dev;
    cd $REPO_PATH;
    mkdir -p docs;
    pandoc README.md -o sphinx/intro.rst;
    sphinx-build sphinx docs;
    cp sphinx/style.css docs/_static/style.css;
    touch docs/.nojekyll;
    mkdir -p docs/resources;
}

x_docs_architecture () {
    # Generate architecture.svg diagram from all import statements
    echo "${CYAN}GENERATING ARCHITECTURE DIAGRAM${CLEAR}\n";
    _x_link_dev;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_architecture( \
    '/home/ubuntu/$REPO/python', \
    'docs/architecture.svg', \
    exclude_regex='test|mock', \
    orient='lr', \
)";
}

x_docs_full () {
    # Generate documentation, coverage report, architecture diagram and code
    # metrics
    x_docs && x_test_coverage && x_docs_architecture && x_docs_metrics;
}

x_docs_metrics () {
    # Generate code metrics report, plots and tables
    echo "${CYAN}GENERATING METRICS${CLEAR}\n";
    _x_link_dev;
    cd $REPO_PATH;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_plots_and_tables('python', 'docs/plots.html', 'docs')"
}

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
    # Install all dependencies of dev/pyproject.toml into /home/ubuntu/dev
    echo "${CYAN}INSTALL DEV${CLEAR}\n";
    _x_workflow_dev "pdm install --no-self --dev -v";
}

x_library_install_prod () {
    # Install all dependencies of prod/pyproject.toml into /home/ubuntu/prod
    echo "${CYAN}INSTALL PROD${CLEAR}\n";
    _x_generate_prod;
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
    # Update /home/ubuntu/dev/pdm.lock file
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

x_test_coverage () {
    # Generate test coverage report
    echo "${CYAN}GENERATING TEST COVERAGE REPORT${CLEAR}\n";
    _x_link_dev;
    cd $REPO_PATH;
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
    cd $REPO_PATH;
    pytest -c docker/dev/pyproject.toml --numprocesses $PROCS python;
}

x_test_fast () {
    # Test all code excepts tests marked with SKIP_SLOWS_TESTS decorator
    echo "${CYAN}FAST TESTING DEV${CLEAR}\n";
    _x_link_dev;
    cd $REPO_PATH;
    SKIP_SLOW_TESTS=true \
    pytest -c docker/dev/pyproject.toml --numprocesses $PROCS python;
}

x_test_lint () {
    # Run linting and type checking
    _x_link_dev;
    cd $REPO_PATH;
    echo "${CYAN}LINTING${CLEAR}\n";
    flake8 python --config docker/config/flake8.ini;
    echo "${CYAN}TYPE CHECKING${CLEAR}\n";
    mypy python --config-file docker/dev/pyproject.toml;
}

x_test_prod () {
    # Run tests across all support python versions
    _x_generate_prod;
    x_build_test;
    _x_link_prod;
    echo "${CYAN}TESTING PROD${CLEAR}\n";
    cd $BUILD_PATH/repo;
    tox --parallel -v;
}

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
