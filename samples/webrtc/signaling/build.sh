#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$DOCKERFILE_DIR")

# Build WebRTC signaling server docker image
echo "---------------------------------------"
echo "Building webrtc_signaling_server container."
echo "---------------------------------------"
TAG=webrtc_signaling_server:latest
BASE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
docker build $SOURCE_DIR/signaling/. $BASE_BUILD_ARGS -t $TAG
