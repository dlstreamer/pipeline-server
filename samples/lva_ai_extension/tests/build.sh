#!/bin/bash
WORK_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$WORK_DIR/../../..")
LVA_DIR=$(dirname $WORK_DIR)
echo $WORK_DIR
echo $ROOT_DIR
echo $LVA_DIR
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

# Build VA Serving
$ROOT_DIR/docker/build.sh --framework gstreamer --create-service false --base openvino/ubuntu18_runtime:2020.4 --pipelines samples/lva_ai_extension/pipelines --models samples/lva_ai_extension/models/models.list.yml

# Add LVA extension layer
docker build -f $LVA_DIR/docker/Dockerfile $SAMPLE_BUILD_ARGS -t video-analytics-serving-lva-ai-extension $LVA_DIR

# Add tests layer
docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t video-analytics-serving-lva-tests $WORK_DIR
