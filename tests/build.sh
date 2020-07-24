#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

DIR=$(dirname $(readlink -f "$0"))
. "$DIR/../docker/build.sh" $@ --dockerfile-dir "$DIR/../docker"

#VA_SERVING_TAG is used to explicitly define the TAG that was used for building VA Serving
#TAG variable is set through the build script above
VA_SERVING_TAG=$TAG

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host --no-cache"
BUILD_ARGS+=" --build-arg BASE=$VA_SERVING_TAG "
TAG="$VA_SERVING_TAG-tests:latest"

docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR
