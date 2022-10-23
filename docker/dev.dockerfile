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
        python3.10-venv

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
RUN mkdir -p /home/ubuntu/.pdm/cache && \
    chown -R ubuntu:ubuntu /home/ubuntu/.pdm
USER ubuntu

ENV REPO='lunchbox'
ENV REPO_ENV=True
ENV PYTHONPATH ":/home/ubuntu/$REPO/python:/home/ubuntu/.pdm/__pypackages__/3.10/lib"
ENV PATH "${PATH}:/home/ubuntu/.local/bin:/home/ubuntu/.pdm/__pypackages__/3.10/bin"

# install python dependencies
COPY pyproject.toml /home/ubuntu/.pdm/pyproject.toml
COPY pdm.toml /home/ubuntu/.pdm/.pdm.toml
RUN echo "\n${CYAN}INSTALL PYTHON DEPENDENCIES${CLEAR}"; \
    cd /home/ubuntu/.pdm && \
    pdm install --no-self --dev -v && \
    rm pyproject.toml && \
    rm .pdm.toml
