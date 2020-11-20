#!/bin/bash -e
WORK_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$WORK_DIR/../../..")
LVA_DIR=$(dirname $WORK_DIR)
CACHE_PREFIX="${1}"
VAS_BASE_IMAGE="${CACHE_PREFIX}openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10"

echo $WORK_DIR
echo $ROOT_DIR
echo $LVA_DIR
echo $VAS_BASE_IMAGE

SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

# Build LVA image
launch "$LVA_DIR/docker/build.sh --remove-gstlibav --base $VAS_BASE_IMAGE"

# Add tests layer
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t video-analytics-serving-lva-tests $WORK_DIR"
