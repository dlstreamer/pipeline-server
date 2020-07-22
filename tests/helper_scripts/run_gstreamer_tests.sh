#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))/..
PYTEST_OUTPUT_GSTREAMER=$WORK_DIR/pytest.gstreamer.txt

echo "Removing previous devcheck output files"
rm -f $PYTEST_OUTPUT_GSTREAMER
  
echo "Running VA Serving Functional Tests (GStreamer)"
if [[ "$(docker images -q video-analytics-serving-gstreamer-tests:latest 2> /dev/null)" == "" ]]; then
  # do something
  echo "error, test image does not exist. Please build gstreamer test image"
else
$WORK_DIR/../docker/run.sh --image video-analytics-serving-gstreamer-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
--entrypoint ./tests/pytest.sh \
 > $PYTEST_OUTPUT_GSTREAMER
fi

echo "Output result of PyTest GStreamer: $PYTEST_OUTPUT_GSTREAMER"
