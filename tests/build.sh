#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

#Get options passed into script to use with building the test
#Get the TAG that will be used for the base image
#While its not explicitly needed here (if it follows the same principles as
#how FRAMEWORK is set, then this script should be able to refer to it as $TAG)
#it makes it easier to read this script and understand where the tag is coming from
function get_options {
  while :; do
    case $1 in
      --tag)
        if [ "$2" ]; then
          VA_SERVING_TAG=$2
          shift
        else
          error 'ERROR: "--tag" requires a non-empty option argument.'
        fi
        ;;
      "")
        break
	;;
      *)
        ;;
    esac

    shift
  done
}

#Preserve arguments to replace
args=("$@")
get_options "$@"
set -- "${args[@]}"

#Build the VA-Serving image
#FRAMEWORK variable is set through the build script
DIR=$(dirname $(readlink -f "$0"))
. "$DIR/../docker/build.sh" $@ --dockerfile-dir "$DIR/../docker"

#If tag is not used, set VA_SERVING_TAG to default
if [ "$VA_SERVING_TAG" ]; then
  VA_SERVING_TAG=video-analytics-serving-$FRAMEWORK
fi


DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host --no-cache"
BUILD_ARGS+=" --build-arg BASE=$VA_SERVING_TAG "
TAG="$VA_SERVING_TAG-tests:latest"

docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR
