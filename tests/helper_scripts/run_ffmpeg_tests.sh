#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))/..
PYTEST_OUTPUT_FFMPEG=$WORK_DIR/pytest.ffmpeg.txt

echo "Removing previous devcheck output files"
rm -f $PYTEST_OUTPUT_FFMPEG

echo "Running VA Serving Functional Tests (FFmpeg)"
if [[ "$(docker images -q video-analytics-serving-ffmpeg-tests:latest 2> /dev/null)" == "" ]]; then
  # do something
  echo "error, test image does not exist. Please build ffmpeg test image"
else
$WORK_DIR/../docker/run.sh --image video-analytics-serving-ffmpeg-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
--entrypoint ./tests/pytest.sh \
 > $PYTEST_OUTPUT_FFMPEG
fi

echo "Output result of PyTest FFmpeg: $PYTEST_OUTPUT_FFMPEG"
