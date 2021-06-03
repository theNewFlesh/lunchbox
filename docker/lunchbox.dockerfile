FROM ubuntu:20.04

WORKDIR /root

# coloring syntax for headers
ARG CYAN='\033[0;36m'
ARG NO_COLOR='\033[0m'
ARG DEBIAN_FRONTEND=noninteractive

RUN echo "\n${CYAN}REMOVE LOGIN MOTD${NO_COLOR}"; \
    touch ~/.hushlogin

# update ubuntu and install basic dependencies
RUN echo "\n${CYAN}INSTALL GENERIC DEPENDENCIES${NO_COLOR}"; \
    apt update && \
    apt install -y \
        curl \
        git \
        pandoc \
        parallel \
        python3-pip \
        python3-setuptools \
        software-properties-common \
        tree \
        vim \
        wget

# install zsh
RUN echo "\n${CYAN}SETUP ZSH${NO_COLOR}"; \
    apt install -y zsh && \
    curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -o install-oh-my-zsh.sh && \
    echo y | sh install-oh-my-zsh.sh && \
    rm -rf install-oh-my-zsh.sh

# install python3.7 and pip
ADD https://bootstrap.pypa.io/get-pip.py get-pip.py
RUN echo "\n${CYAN}SETUP PYTHON3.7${NO_COLOR}"; \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.7 && \
    python3.7 get-pip.py && \
    rm -rf /root/get-pip.py

# DEBIAN_FRONTEND needed by texlive to install non-interactively
RUN echo "\n${CYAN}INSTALL NODE.JS DEPENDENCIES${NO_COLOR}"; \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt upgrade -y && \
    echo "\n${CYAN}INSTALL JUPYTERLAB DEPENDENCIES${NO_COLOR}"; \
    apt install -y \
        nodejs && \
    rm -rf /var/lib/apt/lists/*

# install python dependencies
COPY ./dev_requirements.txt /root/dev_requirements.txt
COPY ./prod_requirements.txt /root/prod_requirements.txt
RUN echo "\n${CYAN}INSTALL PYTHON DEPENDECIES${NO_COLOR}"; \
    apt update && \
    apt install -y \
        graphviz \
        python3-pydot && \
    pip3.7 install -r dev_requirements.txt && \
    pip3.7 install -r prod_requirements.txt;
RUN rm -rf /root/dev_requirements;

# configure zshrc
WORKDIR /root
COPY ./henanigans.zsh-theme /root/.oh-my-zsh/custom/themes/henanigans.zsh-theme
COPY ./zshrc /root/.zshrc
RUN echo "\n${CYAN}CONFIGURE ZSHRC${NO_COLOR}"; \
    echo 'export PYTHONPATH="/root/lunchbox/python"' >> /root/.zshrc;

# install jupyter lab extensions
ENV NODE_OPTIONS="--max-old-space-size=8192"
RUN echo "\n${CYAN}INSTALL JUPYTER LAB EXTENSIONS${NO_COLOR}"; \
    jupyter labextension install \
    --dev-build=False \
        nbdime-jupyterlab \
        @oriolmirosa/jupyterlab_materialdarker \
        @ryantam626/jupyterlab_sublime \
        @jupyterlab/plotly-extension

ENV PYTHONPATH "${PYTHONPATH}:/root/lunchbox/python"
ENV LANGUAGE "C"
ENV LC_ALL "C"
ENV LANG "C"
