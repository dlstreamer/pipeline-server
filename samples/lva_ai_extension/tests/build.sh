#!/bin/bash
WORK_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$WORK_DIR/../../..")
LVA_DIR=$(dirname $WORK_DIR)
echo $WORK_DIR
echo $ROOT_DIR
echo $LVA_DIR


SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

# Build LVA image
$LVA_DIR/docker/build.sh --remove-gstlibav

VAS_BUILD_EXITCODE=$?
if [ $VAS_BUILD_EXITCODE -eq 0 ]
then
  echo "Successfully built VA parent image..."
else
  echo "Could not build VA parent image! Exit: $VAS_BUILD_EXITCODE" >&2
  exit $VAS_BUILD_EXITCODE
fi

# Add tests layer
docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t video-analytics-serving-lva-tests $WORK_DIR
