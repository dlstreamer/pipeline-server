#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

ARG BASE=dlstreamer-pipeline-server-gstreamer-base
ARG MODELS_COMMAND=do_not_copy_models
ARG PIPELINES_COMMAND=do_not_copy_pipelines
ARG FINAL_STAGE=dlstreamer-pipeline-server-environment

########################################################
# First stage installs dlstreamer-pipeline-server and its dependencies on top of a compatible Media Analytics Base.
# See documentation for more details on requirements for the Media Analytics Base.

FROM ${BASE} as dlstreamer-pipeline-server
ARG FRAMEWORK=gstreamer

# Multi-License Disclaimer
RUN echo "IMPORTANT: This script will build third party components licensed under various open source licenses into your container images. The terms under which those components may be used and distributed can be found with the license document that is provided with those components. Please familiarize yourself with those terms to ensure your distribution of those components complies with the terms of those licenses."

# Switching to root user to create user and install packages
USER root

# Dependencies for OpenVINO
ARG BASE=dlstreamer-pipeline-server-gstreamer-base
ENV PIPELINE_SERVER_BASE=${BASE}
SHELL ["/bin/bash", "-c"]

# Creating user pipeline-server and adding it to groups "video" and "users" to use GPU and VPU
ARG USER=pipeline-server
RUN useradd -ms /bin/bash -G video,audio,users ${USER} -d /home/pipeline-server && \
    chown ${USER} -R /home/pipeline-server /root

RUN if [ -f /opt/intel/openvino/install_dependencies/install_NEO_OCL_driver.sh ]; then \
       /opt/intel/openvino/install_dependencies/install_NEO_OCL_driver.sh -y ; exit 0; \
    fi

RUN if [[ ${PIPELINE_SERVER_BASE} == *"openvino/ubuntu20_data_runtime:2021.2" ]]; then \
    DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    intel-media-va-driver-non-free \
    gstreamer1.0-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ;\
    fi

# Install boost library required for HDDL plugin
RUN if [[ ${PIPELINE_SERVER_BASE} == *"openvino/ubuntu20_data_runtime"* ]]; then \
    DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    libboost-program-options1.71.0 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ;\
    fi

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get upgrade -y -q && \
    apt-get dist-upgrade -y -q && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ;

RUN if [[ ${PIPELINE_SERVER_BASE} == *"openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg"* ]]; then \
    DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    python3 \
    python3-setuptools \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* ;\
    fi

COPY ./requirements.txt /
RUN pip3 install --upgrade pip --no-cache-dir -r /requirements.txt
RUN rm -f /requirements.txt

# Pipeline Server Python Modules
COPY ./server /home/pipeline-server/server
COPY ./client /home/pipeline-server/client
COPY --chown=pipeline-server ./tools /home/pipeline-server/tools

# Copy GVA Python extensions
COPY ./extensions /home/pipeline-server/extensions

# Media Analytics Framework set via environment variable
ENV FRAMEWORK=${FRAMEWORK}
WORKDIR /home/pipeline-server
########################################################

########################################################
# Second stage copies models from build context if specified via build argument
# Selective copy is controlled via creating a stage with and without the copy command.
# The stage used in the final image is controlled via the build argument MODEL_COMMAND.

# Creates a stage that does not copy models
FROM dlstreamer-pipeline-server as do_not_copy_models

# Creates a stage that copies models from the build context
FROM dlstreamer-pipeline-server as copy_models
ONBUILD ARG MODELS_PATH
ONBUILD ENV MODELS_PATH=${MODELS_PATH}
ONBUILD COPY ${MODELS_PATH} /home/pipeline-server/models

# Stage that is used is controlled via MODELS_COMMAND build argument
FROM ${MODELS_COMMAND} as dlstreamer-pipeline-server-with-models
########################################################

########################################################
# Third stage copies pipelines from build context if specified via build argument.
# Selective copy is controlled via creating a stage with and without the copy command.
# The stage used in the final image is controlled via the build argument PIPELINES_COMMAND.

# Creates a stage that does not copy pipelines
FROM dlstreamer-pipeline-server-with-models as do_not_copy_pipelines

# Creates a stage that copies pipelines from the build context
FROM dlstreamer-pipeline-server-with-models as copy_pipelines
ONBUILD ARG PIPELINES_PATH
ONBUILD ENV PIPELINES_PATH=${PIPELINES_PATH}
ONBUILD COPY ${PIPELINES_PATH} /home/pipeline-server/pipelines

# Stage that is used is controlled via PIPELINES_COMMAND build argument
FROM ${PIPELINES_COMMAND} as dlstreamer-pipeline-server-with-models-and-pipelines
########################################################

########################################################
# Fourth stage creates the final image either with a default command or with a default entrypoint.
# Final stage is controlled by the FINAL_STAGE build argument.

FROM dlstreamer-pipeline-server-with-models-and-pipelines as dlstreamer-pipeline-server-library
ONBUILD RUN rm -rf /home/pipeline-server/server/__main__.py
ONBUILD RUN rm -rf /home/pipeline-server/server/rest_api

FROM dlstreamer-pipeline-server-with-models-and-pipelines as dlstreamer-pipeline-server-service

# Dependencies installed via pip
ONBUILD COPY ./requirements.service.txt /
ONBUILD RUN pip3 install  --no-cache-dir -r /requirements.service.txt
ONBUILD RUN rm -f /requirements.service.txt
ONBUILD ENTRYPOINT ["python3", "-m", "server"]

FROM ${FINAL_STAGE} as deploy

ARG USER=pipeline-server

ENV PYTHONPATH=$PYTHONPATH:/home/pipeline-server

# Prepare XDG_RUNTIME_DIR
ENV XDG_RUNTIME_DIR=/home/.xdg_runtime_dir
RUN mkdir -p -m g+s $XDG_RUNTIME_DIR && chown ${USER}:users $XDG_RUNTIME_DIR

USER ${USER}
