#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FRAMEWORK=gstreamer
BUILD_VASERVING_IMAGE=true

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --framework)
        if [ "$2" ]; then
          FRAMEWORK=$2
          shift
        else
          error 'ERROR: "--framework" requires a non-empty option argument.'
        fi
        ;;
      --build-vaserving-image)
        if [ "$2" ]; then
          BUILD_VASERVING_IMAGE=$2
          shift
        else
          error 'ERROR: "--build-vaserving-image" requires a non-empty option argument.'
        fi
        ;;
      *)
        break
        ;;
    esac

    shift
  done
}

function show_help {
  echo "usage: build.sh"
  echo "  [ --framework : Framework to build test image]"
  echo "  [ --build-vaserving-image : Build VA-Serving image as part of this script]"
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

if $BUILD_VASERVING_IMAGE; then
  DIR=$(dirname $(readlink -f "$0"))
  . "$DIR/../docker/build.sh" --framework $FRAMEWORK --dockerfile-dir "$DIR/../docker"
fi

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host --no-cache"
VA_SERVING_IMAGE=video-analytics-serving-$FRAMEWORK
BUILD_ARGS+=" --build-arg BASE=$VA_SERVING_IMAGE "
TAG="video-analytics-serving-${FRAMEWORK}-tests"

docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR
