#!/bin/bash -e

SCRIPT_DIR=$(dirname $(readlink -f "$0"))
WORK_DIR="$SCRIPT_DIR/docker"
BASE_IMAGE=${BASE_IMAGE:-amr-registry.caas.intel.com/media-analytics/video-analytics-serving:haproxy1}

PIPELINE_SERVER_WORKER_IMAGE=${PIPELINE_SERVER_WORKER_IMAGE:-"localhost:32000/dlstreamer-pipeline-server-worker:latest"}


echo "Building Pipeline Server image with feedback files"

docker build --network=host \
    --build-arg no_proxy --build-arg https_proxy --build-arg socks_proxy --build-arg http_proxy \
    --build-arg BASE=$BASE_IMAGE \
    -t $PIPELINE_SERVER_WORKER_IMAGE $WORK_DIR


echo "pushing $PIPELINE_SERVER_WORKER_IMAGE into k8s registry..."
docker push $PIPELINE_SERVER_WORKER_IMAGE
