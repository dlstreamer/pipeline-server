#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$DOCKERFILE_DIR")

# Usage:
# ./build.sh  [--remove-volumes]
# Pass --remove-volumes to forcibly remove local volume storage used by Grafana
# full rebuild (requires sudo)

# Prepare Pipeline Server MVP Dashboard
echo "---------------------------------------"
echo "Preparing Pipeline Server MVP Dashboard."
echo "---------------------------------------"
ADD_IP_ADDR=$(hostname -I | cut -d' ' -f1)
HTTP_HOST="http:\/\/${ADD_IP_ADDR}:8082"
PS_HOST="http:\/\/${ADD_IP_ADDR}:8080"
mkdir -p $SOURCE_DIR/grafana/content
sed "s/\%HTTP_HOST\%/$HTTP_HOST/g" $SOURCE_DIR/grafana/http-stream-dashboard.json.template > $SOURCE_DIR/grafana/content/http-stream-dashboard.json
sed -i "s/\%PS_HOST\%/$PS_HOST/g" $SOURCE_DIR/grafana/content/http-stream-dashboard.json

# Prepare shared storage mountpoint on local host
if [ "$1" == "--remove-volumes" ]; then
    echo "---------------------------------------"
    echo "Preparing Grafana volume for storage."
    echo "---------------------------------------"
    pushd $SOURCE_DIR
    docker-compose stop webrtc_grafana
    docker-compose rm webrtc_grafana
    vol_exists="$(docker volume ls | grep webrtc_grafana-storage)"
    if [[ "$vol_exists" != "" ]]; then
        echo "Grafana storage volume will be removed/re-created."
        docker volume rm webrtc_grafana-storage
    else
        echo "Grafana storage volume will be re-created."
    fi
    echo "Removing 'grafana-storage' volume mount"
    sudo rm -rf $SOURCE_DIR/grafana/grafana-storage/
    popd
fi
mkdir -p $SOURCE_DIR/grafana/grafana-storage/

# Prepare Grafana container
echo "---------------------------------------"
echo "Building Grafana container w/ plugins."
echo "---------------------------------------"
TAG=webrtc_grafana:latest
BASE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
docker build $SOURCE_DIR/grafana $BASE_BUILD_ARGS -t $TAG
