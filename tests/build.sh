#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

DIR=$(dirname $(readlink -f "$0"))
. "$DIR/../docker/build.sh" $@ --tag video-analytics-serving-test-base --dockerfile-dir "$DIR/../docker"

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host"
BASE_IMAGE=video-analytics-serving-test-base
BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
TAG="video-analytics-serving-${FRAMEWORK}-tests"

docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG --no-cache $SOURCE_DIR
