#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
PYTEST_OUTPUT_FFMPEG=$WORK_DIR/pytest.ffmpeg.txt
PYTEST_OUTPUT_GSTREAMER=$WORK_DIR/pytest.gstreamer.txt
PYLINT_OUTPUT_FNAME=pylint.results.txt
PYLINT_OUTPUT=$WORK_DIR/$PYLINT_OUTPUT_FNAME
#CHECK_TESTS="pytest,pylint"
#FRAMEWORK="ffmpeg,gstreamer"

echo "Removing previous devcheck output files"
rm -f $PYLINT_OUTPUT
rm -f $PYTEST_OUTPUT_FFMPEG
rm -f $PYTEST_OUTPUT_GSTREAMER

echo "Build image for VA Serving FFmpeg scan"
$WORK_DIR/build.sh --framework ffmpeg
  
echo "Build image for VA Serving GStreamer tests"
$WORK_DIR/build.sh --framework gstreamer

echo "Running VA Serving Functional Tests (GStreamer)"
$WORK_DIR/../docker/run.sh --image video-analytics-serving-gstreamer-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
--entrypoint ./tests/pytest.sh \
 > $PYTEST_OUTPUT_GSTREAMER

echo "Running VA Serving Functional Tests (FFmpeg)"
$WORK_DIR/../docker/run.sh --image video-analytics-serving-ffmpeg-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
--entrypoint ./tests/pytest.sh \
 > $PYTEST_OUTPUT_FFMPEG

echo "Running PyLint Scan within FFmpeg container"
$WORK_DIR/../docker/run.sh --image video-analytics-serving-ffmpeg-tests:latest \
-v $WORK_DIR:/home/video-analytics-serving/tests \
-v /tmp/vas:/tmp  \
--entrypoint ./tests/pylint.sh \
--entrypoint-args "$PYLINT_OUTPUT_FNAME"

echo "Output result of PyTest FFmpeg: $PYTEST_OUTPUT_FFMPEG"
#cat $PYTEST_OUTPUT_FFMPEG
echo "Output result of PyTest GStreamer: $PYTEST_OUTPUT_GSTREAMER"
#cat $PYTEST_OUTPUT_GSTREAMER
echo "Output result of PyLint Scan: $PYLINT_OUTPUT"
#cat $PYLINT_OUTPUT
