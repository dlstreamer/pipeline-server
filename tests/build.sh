#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FRAMEWORK=gstreamer
SUFFIX=latest

#Get options passed into script to use with building the test
function get_options {
  while :; do
    case $1 in
      --framework)
        if [ "$2" ]; then
          FRAMEWORK=$2
          shift
        else
          error 'ERROR: "--framework" requires a non-empty option argument.'
        fi
        ;;
      --suffix)
        if [ "$2" ]; then
          SUFFIX=$2
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

#Preserve arguments to replace
args=("$@")
get_options "$@"
set -- "${args[@]}"

DIR=$(dirname $(readlink -f "$0"))
. "$DIR/../docker/build.sh" $@ --dockerfile-dir "$DIR/../docker"

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host --no-cache"
VA_SERVING_IMAGE=video-analytics-serving-$FRAMEWORK
BUILD_ARGS+=" --build-arg BASE=$VA_SERVING_IMAGE "
TAG="video-analytics-serving-${FRAMEWORK}-tests:$SUFFIX"

docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR
