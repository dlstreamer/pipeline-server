#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
PYTEST_OUTPUT_FFMPEG=$WORK_DIR/pytest.ffmpeg.txt
PYTEST_OUTPUT_GSTREAMER=$WORK_DIR/pytest.gstreamer.txt
PYLINT_OUTPUT_FNAME=pylint.results.txt
PYLINT_OUTPUT=$WORK_DIR/$PYLINT_OUTPUT_FNAME
#CHECK_TESTS="pytest,pylint"
#FRAMEWORK="ffmpeg,gstreamer"
RUN_BUILD=true
RUN_GST_TESTS=true
RUN_FFMPEG_TESTS=true
RUN_PYLINT_TESTS=true

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --skip-build)
        RUN_BUILD=false
        ;;
      --skip-gst-tests)
        RUN_GST_TESTS=false
        ;;
      --skip-ffmpeg-tests)
        RUN_FFMPEG_TESTS=false
        ;;
      --skip-pylint-tests)
        RUN_PYLINT_TESTS=false
        ;;
      *)
        break
        ;;
    esac

    shift
  done
}

function show_help {
  echo "usage: run.sh"
  echo "  [ --skip-build : Skip building test image as part of run script]"
  echo "  [ --skip-gst-tests : Skip GStreamer tests]"
  echo "  [ --skip-ffmpeg-tests : Skip FFMPEG tests]"
  echo "  [ --skip-pylint-tests : Skip Pylint tests]"
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

echo "Removing previous devcheck output files"
rm -f $PYLINT_OUTPUT
rm -f $PYTEST_OUTPUT_FFMPEG
rm -f $PYTEST_OUTPUT_GSTREAMER

if $RUN_BUILD; then
  echo "Build image for VA Serving FFmpeg scan"
  $WORK_DIR/build.sh --framework ffmpeg
  
  echo "Build image for VA Serving GStreamer tests"
  $WORK_DIR/build.sh --framework gstreamer
else
  echo "Skipping build of test images"
fi

if $RUN_GST_TESTS; then
  # Running VA Serving Functional Tests (GStreamer)
  $WORK_DIR/run_gstreamer_tests.sh
else
  echo "Skipping Gstreamer tests"
fi

if $RUN_FFMPEG_TESTS; then
  # Running VA Serving Functional Tests (FFmpeg)
  $WORK_DIR/run_ffmpeg_tests.sh
else
  echo "Skipping FFMPEG tests"
fi

if $RUN_PYLINT_TESTS; then
  # Running PyLint Scan within FFmpeg container
  $WORK_DIR/run_pylint_tests.sh
else
  echo "Skipping Pylint tests"
fi
