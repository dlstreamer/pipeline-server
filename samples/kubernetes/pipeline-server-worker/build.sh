#!/bin/bash -e

SCRIPT_DIR=$(dirname $(readlink -f "$0"))
WORK_DIR="$SCRIPT_DIR/docker"
BASE_IMAGE=${BASE_IMAGE}
PIPELINE_SERVER_WORKER_IMAGE="localhost:32000/dlstreamer-pipeline-server-worker:latest"
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

if [ ! -z "$BASE_IMAGE" ]; then
    echo "Building Pipeline Server Worker image using Base image $BASE_IMAGE"
    BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
fi

echo "Building Pipeline Server image with feedback files"
docker build --network=host $BUILD_ARGS -t $PIPELINE_SERVER_WORKER_IMAGE $WORK_DIR

echo "pushing $PIPELINE_SERVER_WORKER_IMAGE into k8s registry..."
docker push $PIPELINE_SERVER_WORKER_IMAGE
