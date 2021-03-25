#!/bin/bash

ENTRYPOINT_ARGS=
DOCKER_RUN_OPTIONS=
TESTS_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $TESTS_DIR)
INTERACTIVE=--non-interactive
FRAMEWORK=gstreamer
DOCKER_TESTS_DIR="/home/video-analytics-serving/tests"
RESULTS_DIR="results"
PYTEST_GSTREAMER_RESULTS_DIR="$RESULTS_DIR/pytest/gstreamer"
PYTEST_FFMPEG_RESULTS_DIR="$RESULTS_DIR/pytest/ffmpeg"
PYLINT_RESULTS_DIR="$RESULTS_DIR/pylint"
PYBANDIT_RESULTS_DIR="$RESULTS_DIR/pybandit"
CLAMAV_RESULTS_DIR="$RESULTS_DIR/clamav"

# Default selected as gstreamer pytests
FRAMEWORK=gstreamer
OUTPUT_DIR="$PYTEST_GSTREAMER_RESULTS_DIR"
SELECTED="--pytest-gstreamer"
ENTRYPOINT="--entrypoint ./tests/entrypoint/pytest.sh"

# For default gstreamer image, it requires extra permisions to generate coverage report. needs to investigate more.
# TODO: fix user permsion issue for generating reports
USER="--user root"

function show_help {
  echo "usage: run.sh (options are exclusive)"
  echo "  [ --pytest-gstreamer : Run gstreamer tests ]"
  echo "  [ --pytest-ffmpeg: Run ffmpeg tests ] "
  echo "  [ --pylint : Run pylint scan ] "
  echo "  [ --pybandit: Run pybandit scan ] "
  echo "  [ --clamav : Run antivirus scan ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

ARGS=$@
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    --pytest-gstreamer)
      ;;
    --pytest-ffmpeg)
      OUTPUT_DIR="$PYTEST_FFMPEG_RESULTS_DIR"
      FRAMEWORK=ffmpeg
      SELECTED="$1"
      ;;
    --pylint)
      OUTPUT_DIR="$PYLINT_RESULTS_DIR"
      ENTRYPOINT="--entrypoint ./tests/entrypoint/pylint.sh"
      SELECTED="$1"
      ;;
    --pybandit)
      OUTPUT_DIR="$PYBANDIT_RESULTS_DIR"
      ENTRYPOINT="--entrypoint ./tests/entrypoint/pybandit.sh"
      SELECTED="$1"
      ;;
    --clamav)
      OUTPUT_DIR="$CLAMAV_RESULTS_DIR"
      ENTRYPOINT="--entrypoint ./tests/entrypoint/clamav.sh"
      SELECTED="$1"
      ;;
    *)
      break
      ;;
  esac
  shift
done

IMAGE=video-analytics-serving-${FRAMEWORK}-tests:latest

DOCKER_RESULTS_DIR="$DOCKER_TESTS_DIR/$OUTPUT_DIR"
LOCAL_RESULTS_DIR="$TESTS_DIR/$OUTPUT_DIR"

echo "running $SELECTED"
ENVIRONMENT="-e RESULTS_DIR=$DOCKER_RESULTS_DIR"

mkdir -p "$LOCAL_RESULTS_DIR"

VOLUME_MOUNT="-v $LOCAL_RESULTS_DIR:$DOCKER_RESULTS_DIR "

$SOURCE_DIR/docker/run.sh --image $IMAGE --enable-rtsp --framework $FRAMEWORK $USER $VOLUME_MOUNT $ENVIRONMENT $INTERACTIVE $ENTRYPOINT "$@"
