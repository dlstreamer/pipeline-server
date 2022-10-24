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
LOCAL_CLIENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(dirname $LOCAL_CLIENT_DIR)
ARGS=
ENV_CERT=
MQTT_CLUSTER_BROKER=

error() {
    printf '%s\n' "$1" >&2
    exit 1
}

while [[ "$#" -ge 0 ]]; do
    case $1  in
            --server-cert)
                if [ "$2" ]; then
                    VOLUME_MOUNT="$VOLUME_MOUNT -v $2:/etc/ssl/certs/server.crt "
                    ENV_CERT=/etc/ssl/certs/server.crt
                    shift
                else
                    error 'ERROR: "--server-cert" requires an argument.'
                fi
                ;;
            --mqtt-cluster-broker)
                if [ "$2" ]; then
                    MQTT_CLUSTER_BROKER=$2
                    shift
                else
                    error 'ERROR: "--mqtt-cluster-broker" requires an argument.'
                fi
                ;;
            *)
                ARGS="${ARGS} ${1}"
                ;;
        esac
    if [[ "$#" -eq 0 ]];
    then
        break
    fi
    shift
done
ENTRYPOINT_ARGS="$PIPELINE_SERVER_ROOT/client $ARGS"

"$ROOT_DIR/docker/run.sh" $INTERACTIVE --name \"\" --network host --image  $IMAGE $VOLUME_MOUNT -e "ENV_CERT=${ENV_CERT}" -e "MQTT_CLUSTER_BROKER=${MQTT_CLUSTER_BROKER}" -e "REQUESTS_CA_BUNDLE=${ENV_CERT}" --entrypoint $ENTRYPOINT --entrypoint-args "$ENTRYPOINT_ARGS"
