# EXPORTS-----------------------------------------------------------------------
export PATH=:/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/bin
export PYTHONPATH=/home/ubuntu/lunchbox/python:/home/ubuntu/.local/share/pdm/venv/lib/python3.10/site-packages/pdm/pep582:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/lib
export REPO_ENV="True"
export REPO="lunchbox"
export REPO_PATH="/home/ubuntu/$REPO"
export BUILD_PATH="/home/ubuntu/build"
export DEV_SOURCE="$REPO_PATH/docker/dev"
export DEV_TARGET="/home/ubuntu/dev"
export PROD_SOURCE="$REPO_PATH/docker/prod"
export PROD_TARGET="/home/ubuntu/prod"
export PROCS=`python3 -c 'import os; print(os.cpu_count())'`
export PROD_PYTHON_VERSION=">=3.7"
export X_TOOLS_PATH="$REPO_PATH/docker/x-tools.sh"

# HELPER-FUNCTIONS--------------------------------------------------------------
_x-link () {
    # Link given __pypackages__ directory to /home/ubuntu/__pypackages__
    # args: pypackages directory
    ln -sf $1 /home/ubuntu/__pypackages__;
}

_x-link-dev () {
    # Link /home/ubuntu/dev/__pypackages__ to /home/ubuntu/__pypackages__
    _x-link $DEV_TARGET/__pypackages__;
}

_x-link-prod () {
    # Link /home/ubuntu/prod/__pypackages__ to /home/ubuntu/__pypackages__
    _x-link $PROD_TARGET/__pypackages__;
}

_x-dir-copy () {
    # copy all contents of source into target, skipping __pypackages__ directory
    # args: source, target
    ls -pA $1 | grep -v '/' \
    | parallel "cp --force $1/{} $2/{}";
}

_x-from-dev-path () {
    # Copy lunchbox/docker/dev to /home/ubuntu/dev
    _x-dir-copy $DEV_SOURCE $DEV_TARGET;
}

_x-from-prod-path () {
    # Copy lunchbox/docker/prod to /home/ubuntu/prod
    _x-dir-copy $PROD_SOURCE $PROD_TARGET;
}

_x-to-dev-path () {
    # Copy /home/ubuntu/dev to lunchbox/docker/dev
    _x-dir-copy $DEV_TARGET $DEV_SOURCE;
}

_x-to-prod-path () {
    # Copy /home/ubuntu/prod to lunchbox/docker/prod
    _x-dir-copy $PROD_TARGET $PROD_SOURCE;
}

_x-dev-workflow () {
    # Copies docker/dev to ~/dev, run a given command, and copies ~/dev bask to docker/dev
    # args: command string
    local CWD=`pwd`;
    _x-link-dev;
    _x-dir-copy $DEV_SOURCE $DEV_TARGET;
    cd $DEV_TARGET;
    eval "$1";
    _x-dir-copy $DEV_TARGET $DEV_SOURCE;
    cd $CWD;
}

_x-build () {
    # Build production version of repo for publishing
    # args: type (test or prod)
    _x-link-dev;
    cd $REPO_PATH;
    rm -rf $BUILD_PATH;
    python3 docker/rolling_pin_command.py docker/build.yaml --groups base,$1;
}

# TASK-FUNCTIONS----------------------------------------------------------------
x-add-package () {
    # Add a given package to a given dependency group
    # args: package, group
    _x-from-dev-path;
    cd $DEV_TARGET;
    if [[ $2 == 'none' ]] then
        pdm add $1 -v;
    else
        pdm add -dG $2 $1 -v;
    fi;
    _x-to-dev-path;
}

x-architecture () {
    # Generate architecture.svg diagram from all import statements
    _x-link-dev;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_architecture( \
    '/home/ubuntu/$REPO/python', \
    'docs/architecture.svg', \
    exclude_regex='test|mock', \
    orient='lr', \
)";
}

x-build-prod () {
    # Build production version of repo for publishing
    _x-build prod;
}

x-build-test () {
    # Build test version of repo for tox testing
    _x-build test;
}

x-coverage () {
    # Generate test coverage report
    _x-link-dev;
    cd $REPO_PATH;
    mkdir -p docs;
    pytest \
        -c docker/pytest.ini \
        --numprocesses $PROCS \
        --cov=python \
        --cov-config=docker/pytest.ini \
        --cov-report=html:docs/htmlcov \
        python;
}

x-docs () {
    # Generate sphinx documentation
    _x-link-dev;
    cd $REPO_PATH;
    mkdir -p docs;
    pandoc README.md -o sphinx/intro.rst;
    sphinx-build sphinx docs;
    cp sphinx/style.css docs/_static/style.css;
    touch docs/.nojekyll;
    mkdir -p docs/resources;
}

x-fast-test () {
    # Test all code excepts tests marked with SKIP_SLOWS_TESTS decorator
    _x-link-dev;
    cd $REPO_PATH;
    SKIP_SLOW_TESTS=true \
    pytest \
        -c docker/pytest.ini \
        --numprocesses $PROCS \
        python;
}

x-full-docs () {
    # Generate documentation, coverage report, architecture diagram and code metrics
    x-docs && x-coverage && x-architecture && x-metrics;
}

x-install-dev () {
    # Install all dependencies of dev/pyproject.toml into /home/ubuntu/dev
    _x-dev-workflow "pdm install --no-self --dev -v";
}

x-install-prod () {
    # Install all dependencies of prod/pyproject.toml into /home/ubuntu/prod
    _x-link-dev;
    _x-from-prod-path;
    python3 \
        docker/generate_pyproject.py \
            docker/dev/pyproject.toml \
            "$PROD_PYTHON_VERSION" \
            --groups test \
        > $PROD_TARGET/pyproject.toml;
    cd $PROD_TARGET;
    pdm install --no-self --dev -v;
    _x-to-prod-path;
}

x-lab () {
    # Run jupyter lab server
    _x-link-dev;
    jupyter lab --allow-root --ip=0.0.0.0 --no-browser;
}

x-lint () {
    # Run linting and type checking
    _x-link-dev;
    cd $REPO_PATH;
    echo LINTING;
    flake8 python --config docker/flake8.ini;
    echo TYPE CHECKING;
    mypy python --config-file docker/mypy.ini;
}

x-lock () {
    # Update /home/ubuntu/dev/pdm.lock file
    _x-dev-workflow "pdm lock -v";
}

x-metrics () {
    # Generate code metrics report, plots and tables
    _x-link-dev;
    cd $REPO_PATH;
    python3 -c "import rolling_pin.repo_etl as rpo; \
rpo.write_repo_plots_and_tables('python', 'docs/plots.html', 'docs')"
}

x-package () {
    # Generate pip package of repo in /home/ubuntu/build/repo
    x-install-prod;
    x-build-prod;
    cd $BUILD_PATH/repo;
    pdm build -v;
}

x-publish () {
    # Publish pip package of repo to PyPi
    # args: user, password, comment
    x-package;
    cd $BUILD_PATH/repo;
    pdm publish \
        --repository https://test.pypi.org/legacy \
        --no-build \
        --username $1 \
        --password $2 \
        --comment $3 \
        --verbose;
}

x-python () {
    # Run python session with dev dependencies
    _x-link-dev;
    python3.10;
}

x-remove-package () {
    # Remove a given package from a given dependency group
    # args: package, group
    _x-from-dev-path;
    cd $DEV_TARGET;
    if [[ $2 == 'none' ]] then
        pdm remove $1 -v;
    else
        pdm remove -dG $2 $1 -v;
    fi;
    _x-to-dev-path;
}

x-test () {
    # Run all tests
    _x-link-dev;
    cd $REPO_PATH;
    pytest \
       -c docker/pytest.ini \
       --numprocesses $PROCS \
       python;
}

x-tox () {
    # Run tests across all support python versions
    x-build-test;
    _x-link-prod;
    unset REPO_ENV;
    cd $BUILD_PATH/repo;
    tox;
}

x-version () {
    # Full resolution of repo: dependencies, linting, tests, docs, etc
    _x-link-dev;
    x-lint;
    x-install-dev;
    x-full-docs;
}

x-version-bump-major () {
    # Bump repo's major version
    _x-dev-workflow "pdm bump major";
}

x-version-bump-minor () {
    # Bump repo's minor version
    _x-dev-workflow "pdm bump minor";
}

x-version-bump-patch () {
    # Bump repo's patch version
    _x-dev-workflow "pdm bump patch";
}
