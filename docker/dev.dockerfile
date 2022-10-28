FROM ubuntu:22.04 AS base

USER root

# coloring syntax for headers
ENV CYAN='\033[0;36m'
ENV CLEAR='\033[0m'
ENV DEBIAN_FRONTEND='noninteractive'

# setup ubuntu user
ARG UID_='1000'
ARG GID_='1000'
RUN echo "\n${CYAN}SETUP UBUNTU USER${CLEAR}"; \
    addgroup --gid $GID_ ubuntu && \
    adduser \
        --disabled-password \
        --gecos '' \
        --uid $UID_ \
        --gid $GID_ ubuntu && \
    usermod -aG root ubuntu
WORKDIR /home/ubuntu

# update ubuntu and install basic dependencies
RUN echo "\n${CYAN}INSTALL GENERIC DEPENDENCIES${CLEAR}"; \
    apt update && \
    apt install -y \
        curl \
        git \
        graphviz \
        npm \
        pandoc \
        parallel \
        software-properties-common \
        tree \
        vim \
        wget

RUN echo "\n${CYAN}INSTALL PYTHON${CLEAR}"; \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y \
        python3-pydot \
        python3.10-dev \
        python3.10-distutils \
        python3.10-venv \
        python3.9-dev \
        python3.9-distutils \
        python3.9-venv \
        python3.8-dev \
        python3.8-distutils \
        python3.8-venv \
        python3.7-dev \
        python3.7-distutils \
        python3.7-venv

RUN echo "\n${CYAN}INSTALL PIP${CLEAR}"; \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.10 get-pip.py && \
    chown -R ubuntu:ubuntu get-pip.py && \
    pip3.10 install --upgrade pip

# install zsh
RUN echo "\n${CYAN}SETUP ZSH${CLEAR}"; \
    apt install -y zsh && \
    curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh \
        -o install-oh-my-zsh.sh && \
    echo y | sh install-oh-my-zsh.sh && \
    mkdir -p /root/.oh-my-zsh/custom/plugins && \
    cd /root/.oh-my-zsh/custom/plugins && \
    git clone https://github.com/zdharma-continuum/fast-syntax-highlighting && \
    git clone https://github.com/zsh-users/zsh-autosuggestions && \
    npm i -g zsh-history-enquirer --unsafe-perm && \
    cd /home/ubuntu && \
    cp -r /root/.oh-my-zsh /home/ubuntu/ && \
    chown -R ubuntu:ubuntu \
        .oh-my-zsh \
        install-oh-my-zsh.sh && \
    echo 'UTC' > /etc/timezone

USER ubuntu
ENV PATH="/home/ubuntu/.local/bin:$PATH"
COPY ./henanigans.zsh-theme .oh-my-zsh/custom/themes/henanigans.zsh-theme

ENV LANG "C.UTF-8"
ENV LANGUAGE "C.UTF-8"
ENV LC_ALL "C.UTF-8"
# ------------------------------------------------------------------------------

FROM base AS dev

USER ubuntu
WORKDIR /home/ubuntu

RUN echo "\n${CYAN}INSTALL PDM${CLEAR}"; \
    curl -sSL \
        https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py \
    | python3.10 - && \
    mkdir -p /home/ubuntu/.oh-my-zsh/custom/completions && \
    pdm completion zsh > /home/ubuntu/.oh-my-zsh/custom/completions/_pdm

USER root
RUN echo "\n${CYAN}CREATE DEV AND PROD DIRECTORIES${CLEAR}"; \
    mkdir dev prod && \
    chown ubuntu:ubuntu dev prod
USER ubuntu

# install python dependencies
COPY generate_pyproject.py /home/ubuntu/
COPY dev/pyproject.toml /home/ubuntu/dev/
COPY dev/pdm.lock /home/ubuntu/dev/
COPY dev/pdm.toml /home/ubuntu/dev/.pdm.toml
RUN echo "\n${CYAN}INSTALL PYTHON DEV ENVIRONMENT${CLEAR}"; \
    cd pdm && \
    pdm install --no-self --dev -v

COPY prod/pdm.lock /home/ubuntu/prod/
COPY prod/pdm.toml /home/ubuntu/prod/.pdm.toml
RUN echo "\n${CYAN}INSTALL PYTHON PROD ENVIRONMENT${CLEAR}"; \
    pip3.10 install toml && \
    python3 ./generate_pyproject.py \
        ./dev/pyproject.toml ">=3.7" --prod > ./prod/pyproject.toml && \
    cd prod && \
    pdm install --no-self -v

RUN echo "\n${CYAN}SYMLINK ~/PDM TO ~/.LOCAL${CLEAR}"; \
    mv /home/ubuntu/.local /tmp/local && \
    ln -s /home/ubuntu/dev/py310/__pypackages__/3.10 /home/ubuntu/.local && \
    mv /tmp/local/share/pdm /home/ubuntu/.local/share/pdm && \
    rm -rf /tmp/local

ENV REPO='lunchbox'
ENV REPO_ENV=True
ENV PYTHONPATH ":/home/ubuntu/.local/lib/pdm/pep582:/home/ubuntu/.local/lib:/home/ubuntu/$REPO/python"
ENV PATH "${PATH}:/home/ubuntu/.local/bin"
