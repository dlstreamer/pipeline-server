#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
TOOLS_DIR=$(dirname "$SCRIPT_DIR")
SOURCE_DIR=$(dirname "$TOOLS_DIR")
OUTPUT_DIR=$(realpath $( pwd ))
FORCE=
RUN_PREFIX=
OPEN_MODEL_ZOO_TOOLS_IMAGE=${OPEN_MODEL_ZOO_TOOLS_IMAGE:-"${CACHE_PREFIX}openvino/ubuntu20_data_dev"}
OPEN_MODEL_ZOO_VERSION=${OPEN_MODEL_ZOO_VERSION:-"2021.4.2"}
NAME="video-analytics-serving-model-downloader"

DL_STREAMER_VERSION=
MODE=
MODEL_LIST=$SOURCE_DIR/"models_list/models.list.yml"
DRY_RUN=
NON_INTERACTIVE=

show_help() {
  echo "usage: model_downloader.sh"
  echo "  [--output absolute path where to save models]"
  echo "  [--model-list input file with model names and properties]"
  echo "  [--force force download and conversion of existing models]"
  echo "  [--open-model-zoo-version specify the version of openvino image to be used for downloading models from Open Model Zoo]"
  echo "  [--dry-run print commands without executing]"
  exit 0
}

error() {
  printf '%s %s\n' "$1" "$2" >&2
  exit 1
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | -\? | --help)
        show_help # Display a usage synopsis.
        exit
        ;;
    --dry-run)
        DRY_RUN="--dry-run"
        ;;
    --force)
        FORCE="--force"
        ;;
    --open-model-zoo-image)
        if [ "$2" ]; then
            OPEN_MODEL_ZOO_TOOLS_IMAGE=$2
            shift
        else
            error 'ERROR: "--open-model-zoo-image" requires an argument.'
        fi
        ;;
    --open-model-zoo-version)
        if [ "$2" ]; then
            OPEN_MODEL_ZOO_VERSION=$2
            shift
        else
            error 'ERROR: "--open-model-zoo-version" requires an argument.'
        fi
        ;;
    --output) # Takes an option argument; ensure it has been specified.
        if [ "$2" ]; then
            OUTPUT_DIR=$2
            shift
        else
            error 'ERROR: "--output" requires a non-empty option argument.'
        fi
        ;;
    --model-list)
        if [ "$2" ]; then
            MODEL_LIST=$(realpath $2)
            shift
        else
            error 'ERROR: "--model-list" requires a non-empty option argument.'
        fi
        ;;
    --)
        shift
        break
        ;;
    -?*)
        error 'ERROR: Unknown option: ' $1
        ;;
    ?*)
        error 'ERROR: Unknown option: ' $1
        ;;
    *)
        break
        ;;
    esac
    shift
done

YML_DIR=$(dirname "${MODEL_LIST}")
YML_FILE_NAME=$(basename "${MODEL_LIST}")
VOLUME_MOUNT+="-v $TOOLS_DIR:/home/video-analytics-serving/tools -v $YML_DIR:/models_yml -v $OUTPUT_DIR:/output"

case $OPEN_MODEL_ZOO_VERSION in
    2020.4)
        DL_STREAMER_VERSION="v1.1.0"
        ;;
    2021.1)
        DL_STREAMER_VERSION="v1.2.1"
        ;;
    2021.2)
        DL_STREAMER_VERSION="v1.3"
        ;;
    2021.3*)
        DL_STREAMER_VERSION="v1.4.1"
        ;;
    2021.4*)
        DL_STREAMER_VERSION="v1.5"
        ;;
    *)
        error 'ERROR: Unknown Open Model Zoo version: ' $OPEN_MODEL_ZOO_VERSION
esac

if [ ! -z "$TEAMCITY_VERSION" ]; then
    NON_INTERACTIVE=--non-interactive
fi

if [ ! -d "$OUTPUT_DIR/models" ]; then
    mkdir $OUTPUT_DIR/models
    echo "Created output models folder as UID: $UID"
fi

$SOURCE_DIR/docker/run.sh --user "$UID" -e HOME=/tmp $NON_INTERACTIVE --name $NAME --image $OPEN_MODEL_ZOO_TOOLS_IMAGE:$OPEN_MODEL_ZOO_VERSION $VOLUME_MOUNT $DRY_RUN --entrypoint /bin/bash --entrypoint-args "\"-i\" \"-c\" \"pip3 install -r /home/video-analytics-serving/tools/model_downloader/requirements.txt ; python3 -u /home/video-analytics-serving/tools/model_downloader --model-proc-version $DL_STREAMER_VERSION --model-list /models_yml/$YML_FILE_NAME --output /output $FORCE\""
