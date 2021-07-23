#!/bin/bash

VOLUME_MOUNT=
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

# Custom preparation for build configurations
PREPARE_GROUND_TRUTH=${PREPARE_GROUND_TRUTH:-false}
PREPARE_PERFORMANCE=false
DISABLED_TURBO=false
ENVIRONMENT=

function show_help {
  echo "usage: run.sh (options are exclusive)"
  echo "  [ --pytest-gstreamer : Run gstreamer tests ]"
  echo "  [ --pytest-gstreamer-generate : Generate new gstreamer ground truth ]"
  echo "  [ --pytest-gstreamer-performance : Run gstreamer performance tests ]"
  echo "  [ --pytest-ffmpeg: Run ffmpeg tests ] "
  echo "  [ --pytest-ffmpeg-generate: Generate new ffmpeg ground truth ] "
  echo "  [ --pylint : Run pylint scan ] "
  echo "  [ --pybandit: Run pybandit scan ] "
  echo "  [ --clamav : Run antivirus scan ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

function recreate_shared_path() {
  SHARED_PATH=$1
  echo "recreating $SHARED_PATH"
  rm -Rf "$SHARED_PATH"
  mkdir -p "$SHARED_PATH"
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
    --pytest-gstreamer-generate)
      ENTRYPOINT_ARGS+="--entrypoint-args --generate "
      VOLUME_MOUNT+="-v $TESTS_DIR/test_cases:$DOCKER_TESTS_DIR/test_cases "
      PREPARE_GROUND_TRUTH=${PREPARE_GROUND_TRUTH:-true}
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
      ENVIRONMENT+=" -e PYLINTHOME=$DOCKER_TESTS_DIR/$OUTPUT_DIR "
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
    --pytest-gstreamer-performance)
      SELECTED="$1"
      PREPARE_PERFORMANCE=true
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
ENVIRONMENT+="-e RESULTS_DIR=$DOCKER_RESULTS_DIR"

recreate_shared_path "$LOCAL_RESULTS_DIR"
VOLUME_MOUNT+="-v $LOCAL_RESULTS_DIR:$DOCKER_RESULTS_DIR "

# This block is specific to --pytest-gstreamer-performance
if [ $PREPARE_PERFORMANCE == true ]; then
  PSTATE_NO_TURBO="/sys/devices/system/cpu/intel_pstate/no_turbo"
  function disable_turbo {
    echo "Running disable_turbo()"
    PREV_VALUE=$(<${PSTATE_NO_TURBO})
    echo "Current value of ${PSTATE_NO_TURBO}: [$PREV_VALUE]"
    if [ "$PREV_VALUE" == "0" ]; then
      echo "Disabling turbo on this host via intel_pstate/no_turbo"
      if [ "$EUID" -ne 0 ]; then
        echo "Hint: You may wish to update visudo to locally permit NOPASSWD for /usr/bin/tee"
      fi
      echo 1 | sudo tee ${PSTATE_NO_TURBO}
      CURR_VALUE=$(<${PSTATE_NO_TURBO})
      echo "Updated value of ${PSTATE_NO_TURBO} - now: [$CURR_VALUE]"
        if [ "$CURR_VALUE" == "$PREV_VALUE" ]; then
            echo "Failed to update turbo pstate!"
        else
            return 0
        fi
    else
        echo "ERROR expected intel_pstate/no_turbo to be 0 but got $PREV_VALUE!"
    fi
    return 1
  }

  function restore_turbo {
    echo "Running restore_turbo()"
    if [ $DISABLED_TURBO == true ]; then
      echo "Restoring original turbo value on this host via intel_pstate/no_turbo"
      echo $PREV_VALUE | sudo tee ${PSTATE_NO_TURBO}
      CURR_VALUE=$(<${PSTATE_NO_TURBO})
      echo "Restored value of ${PSTATE_NO_TURBO} - now: [$CURR_VALUE]"
    else
      echo "no-op - state was not changed by disable_turbo"
    fi
  }

  trap restore_turbo EXIT
  echo "Preparing for Performance Tests..."
  disable_turbo
  if [ "$?" == "0" ]; then
    echo "disable_turbo was successful!"
    DISABLED_TURBO=true
    # Run as with standard --pytest-gstreamer but constrain to performance
    ENTRYPOINT_ARGS="--entrypoint-args --performance "
    ENTRYPOINT_ARGS+="--entrypoint-args -k "
    ENTRYPOINT_ARGS+="--entrypoint-args performance "
  else
    echo "disable_turbo failed!"
    DISABLED_TURBO=false
  fi
fi

$SOURCE_DIR/docker/run.sh --image $IMAGE --framework $FRAMEWORK $VOLUME_MOUNT $ENVIRONMENT $INTERACTIVE $ENTRYPOINT $ENTRYPOINT_ARGS "$@"

if [ $PREPARE_GROUND_TRUTH == true ]; then
  echo "Renaming .json.generated files to .json in preparation to update ground truth."
  find $TESTS_DIR/test_cases -depth -name "*.json.generated" -exec sh -c 'mv "$1" "${1%.json.generated}.json"' _ {} \;
fi
