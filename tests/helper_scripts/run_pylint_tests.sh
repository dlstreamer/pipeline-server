#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))/..
PYLINT_OUTPUT_FNAME=pylint.results.txt
PYLINT_OUTPUT=$WORK_DIR/$PYLINT_OUTPUT_FNAME

echo "Removing previous devcheck output files"
rm -f $PYLINT_OUTPUT

echo "Running PyLint Scan within FFmpeg container"
if [[ "$(docker images -q video-analytics-serving-ffmpeg-tests:latest 2> /dev/null)" == "" ]]; then
  # do something
  echo "error, test image does not exist. Please build ffmpeg test image"
else
$WORK_DIR/../docker/run.sh --image video-analytics-serving-ffmpeg-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
-v /tmp/vas:/tmp  \
--entrypoint ./tests/pylint.sh \
--entrypoint-args "$PYLINT_OUTPUT_FNAME"
fi

echo "Output result of PyLint Scan: $PYLINT_OUTPUT"
#cat $PYLINT_OUTPUT
