FROM ubuntu:20.04

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
    --gid $GID_ ubuntu
WORKDIR /home/ubuntu

# update ubuntu and install basic dependencies
RUN echo "\n${CYAN}INSTALL GENERIC DEPENDENCIES${CLEAR}"; \
    apt update && \
    apt install -y \
        python3-dev \
        software-properties-common \
        wget

# install python3.7 and pip
RUN echo "\n${CYAN}SETUP PYTHON3.7${CLEAR}"; \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt install --fix-missing -y python3.7 && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python3.7 get-pip.py && \
    rm -rf /home/ubuntu/get-pip.py

USER ubuntu

# install lunchbox
RUN echo "\n${CYAN}INSTALL LUNCHBOX${CLEAR}"; \
    pip3.7 install lunchbox>=0.2.2;

CMD ["/bin/bash"]