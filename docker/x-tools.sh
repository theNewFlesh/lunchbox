# EXPORTS-----------------------------------------------------------------------
export PATH=:/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/bin
export PYTHONPATH=/home/ubuntu/lunchbox/python:/home/ubuntu/.local/share/pdm/venv/lib/python3.10/site-packages/pdm/pep582:/home/ubuntu/.local/lib:/home/ubuntu/dev/__pypackages__/3.10/lib
export REPO_ENV="True"
export REPO="lunchbox"
export REPO_PATH="/home/ubuntu/$REPO"
export BUILD_PATH="/home/ubuntu/build"
export DEV_PATH="$REPO_PATH/docker/dev"
export PROD_PATH="$REPO_PATH/docker/prod"
export PROCS=`python3 -c 'import os; print(os.cpu_count())'`

# HELPER-FUNCTIONS--------------------------------------------------------------
_x-link () {
    # Link given __pypackages__ directory to /home/ubuntu/__pypackages__
    # args: pypackages directory
    ln -sf $1 /home/ubuntu/__pypackages__;
}

_x-link-dev () {
    # Link /home/ubuntu/dev/__pypackages__ to /home/ubuntu/__pypackages__
    _x-link $DEV_PATH/__pypackages__;
}

_x-link-prod () {
    # Link /home/ubuntu/prod/__pypackages__ to /home/ubuntu/__pypackages__
    _x-link $PROD_PATH/__pypackages__;
}

_x-special_copy () {
    # copy all contents of source into target, skipping __pypackages__ directory
    # args: source, target
    find $1 -maxdepth 1 -type f \
    | grep -v __pypackages__ \
    | parallel "cp --force {} $2/";
}

_x-read-dev () {
    # Copy lunchbox/docker/dev to /home/ubuntu/dev
    _x-special_copy $DEV_PATH /home/ubuntu/dev;
}

_x-read-prod () {
    # Copy lunchbox/docker/prod to /home/ubuntu/prod
    _x-special_copy $PROD_PATH /home/ubuntu/prod;
}

_x-write-dev () {
    # Copy /home/ubuntu/dev to lunchbox/docker/dev
    _x-special_copy /home/ubuntu/dev $DEV_PATH;
}

_x-write-prod () {
    # Copy /home/ubuntu/prod to lunchbox/docker/prod
    _x-special_copy /home/ubuntu/prod $PROD_PATH;
}

_x-build () {
    # Build production version of repo for publishing
    # args: type (test or prod)
    _x-link-dev;
    cd $REPO_PATH;
    rm -rf $BUILD_PATH;
    python3 -c "from rolling_pin.conform_etl import ConformETL; \
src = 'docker/build.yaml'; \
ConformETL.from_yaml(src).conform(groups=['base', '$1']) \
";
}

# TASK-FUNCTIONS----------------------------------------------------------------
x-add-package () {
    # Add a given package to a given dependency group
    # args: package, group
    cd $DEV_PATH;
    if [[ $2 == 'none' ]] then
        pdm add $1;
    else
        pdm add -dG $1 $2;
    fi;
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
    cd $DEV_PATH;
    pdm install --no-self --dev -v;
}

x-install-prod () {
    # Install all dependencies of prod/pyproject.toml into /home/ubuntu/prod
    _x-link-dev;
    python3 \
        docker/generate_pyproject.py \
            docker/dev/pyproject.toml \
            '>=3.7' \
            --groups test \
        > $PROD_PATH/pyproject.toml;
    cd $PROD_PATH;
    pdm install --no-self --dev -v;
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
    cd $DEV_PATH;
    pdm lock -v;
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
    cd $DEV_PATH;
    if [[ $2 == 'none' ]] then
        pdm remove $1;
    else
        pdm remove -dG $1 $2;
    fi;
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
    _x-link-dev;
    cd $DEV_PATH;
    pdm bump major;
}

x-version-bump-minor () {
    # Bump repo's minor version
    _x-link-dev;
    cd $DEV_PATH;
    pdm bump minor;
}

x-version-bump-patch () {
    # Bump repo's patch version
    _x-link-dev;
    cd $DEV_PATH;
    pdm bump patch;
}
