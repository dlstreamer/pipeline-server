#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

VOLUME_MOUNT="-v /tmp:/tmp "
IMAGE="dlstreamer-pipeline-server-gstreamer"
PIPELINE_SERVER_ROOT=/home/pipeline-server
ENTRYPOINT="python3"
ENTRYPOINT_ARGS="$PIPELINE_SERVER_ROOT/client $@"
LOCAL_CLIENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(dirname $LOCAL_CLIENT_DIR)

"$ROOT_DIR/docker/run.sh" $INTERACTIVE --name \"\" --network host --image  $IMAGE $VOLUME_MOUNT --entrypoint $ENTRYPOINT --entrypoint-args "$ENTRYPOINT_ARGS"
