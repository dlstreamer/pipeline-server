#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

DIR=$(dirname $(readlink -f "$0"))

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

if [ -z "$PARENT_IMAGE" ]; then
    launch ". $DIR/../docker/build.sh $@ --dockerfile-dir $DIR/../docker"
    # TAG variable is set through the build script on previous line
    PARENT_IMAGE=$TAG
else
    # NOTE: We support building tests on top of any image.
    #       When caller overrides the PARENT_IMAGE, they may also need to supply
    #       appropriate overrides of FRAMEWORK and/or PIPELINES depending on needs.
    if [ -z "$FRAMEWORK" ]; then
        FRAMEWORK="gstreamer"
    fi
    if [ -z "$PIPELINES" ]; then
        PIPELINES=pipelines/$FRAMEWORK
    fi
fi

echo "TEST_IMAGE will build on top of PARENT_IMAGE: $PARENT_IMAGE..."
DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host --no-cache"
BUILD_ARGS+=" --build-arg BASE=$PARENT_IMAGE --build-arg FRAMEWORK=$FRAMEWORK"
TAG="dlstreamer-pipeline-server-$FRAMEWORK-tests:latest"

launch "docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR"

