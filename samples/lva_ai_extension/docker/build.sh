#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

# Build VA Serving
$SAMPLE_DIR/../../docker/build.sh --framework gstreamer --create-service false --base openvino/ubuntu18_runtime:2020.4 --pipelines samples/lva_ai_extension/pipelines --models $SAMPLE_DIR/models/models.list.yml

# Build AI Extention
docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t video-analytics-serving-lva-ai-extension $SAMPLE_DIR
