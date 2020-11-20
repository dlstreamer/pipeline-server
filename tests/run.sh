#!/bin/bash

TESTS_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $TESTS_DIR)
INTERACTIVE=--non-interactive
FRAMEWORK=gstreamer
DOCKER_TESTS_DIR="/home/video-analytics-serving/tests"
RESULTS_DIR="results"
PYTEST_GSTREAMER_RESULTS_DIR="$RESULTS_DIR/pytest/gstreamer"
PYTEST_FFMPEG_RESULTS_DIR="$RESULTS_DIR/pytest/ffmpeg"
PYLINT_RESULTS_DIR="$RESULTS_DIR/pylint"
CLAMAV_RESULTS_DIR="$RESULTS_DIR/clamav"

# Default selected as gstreamer pytests
OUTPUT_DIR="$PYTEST_GSTREAMER_RESULTS_DIR"
IMAGE=video-analytics-serving-gstreamer-tests:latest
SELECTED="--pytest-gstreamer"
ENTRYPOINT="--entrypoint ./tests/entrypoint/pytest.sh"

# For default gstreamer image, it requires extra permisions to generate coverage report. needs to investigate more.
# TODO: fix user permsion issue for generating reports
USER="--user root"

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --pytest-gstreamer)
        shift
        ;;
      --pytest-ffmpeg)
        OUTPUT_DIR="$PYTEST_FFMPEG_RESULTS_DIR"
        IMAGE=video-analytics-serving-ffmpeg-tests:latest
        SELECTED="$1"
        shift
        ;;
      --pylint)
        OUTPUT_DIR="$PYLINT_RESULTS_DIR"
        ENTRYPOINT="--entrypoint ./tests/entrypoint/pylint.sh"
        SELECTED="$1"
        shift
        ;;
      --clamav)
        OUTPUT_DIR="$CLAMAV_RESULTS_DIR"
        ENTRYPOINT="--entrypoint ./tests/entrypoint/clamav.sh"
        SELECTED="$1"
        shift
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
  echo "  [ --pytest-gstreamer : To run gstreamer tests ]"
  echo "  [ --pytest-ffmpeg: To run ffmpeg tests ] "
  echo "  [ --pylint : To run pylint ] "
  echo "  [ --clamav : To run gstreamer antivirus scan ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

DOCKER_RESULTS_DIR="$DOCKER_TESTS_DIR/$OUTPUT_DIR"
LOCAL_RESULTS_DIR="$TESTS_DIR/$OUTPUT_DIR"

echo "running $SELECTED"
ENVIRONMENT="-e RESULTS_DIR=$DOCKER_RESULTS_DIR"

mkdir -p "$LOCAL_RESULTS_DIR"

VOLUME_MOUNT="-v $LOCAL_RESULTS_DIR:$DOCKER_RESULTS_DIR "

$SOURCE_DIR/docker/run.sh --image $IMAGE $USER $VOLUME_MOUNT $ENVIRONMENT $INTERACTIVE $ENTRYPOINT $@
