#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
FRAMEWORK=gstreamer
INTERACTIVE=--non-interactive
CI=
ENVIRONMENT=
ENTRYPOINT_ARGS=
ENTRYPOINT=

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --framework)
        if [ "$2" ]; then
          FRAMEWORK=$2
          shift
        else
          error "Framework expects a value"
        fi
        ;;
      --image)
        if [ "$2" ]; then
          IMAGE=$2
          shift
        else
          error "Image expects a value"
        fi
        ;;
      --pytest-args|--pytest-arg|--pylint-arg)
        if [ "$2" ]; then
          ENTRYPOINT_ARGS+="--entrypoint-args $2 "
          shift
        else
          error "Pytest-args expects a value"
        fi
        ;;
      --pylint)
        ENTRYPOINT="--entrypoint ./tests/pylint.sh"
        ;;
      --dev)
        DEV=--dev
        unset INTERACTIVE
        ;;
      --ci)
        CI="-e TEAMCITY_VERSION=2019.1.3"
        ;;
      -e)
        if [ "$2" ]; then
          ENVIRONMENT+="-e $2 "
          shift
        else
          error "Environment expects a value"
        fi
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
  echo "  [ --image : Specify the image to run the tests on ]"
  echo "  [ --framework : Set the framework for the image, default is gstreamer ] "
  echo "  [ --pylint : Run the pylint test ] "
  echo "  [ --dev : Bash into the test container ] "
  echo "  [ --ci : Output results for Team City integration ] "
  echo "  [ -e : Add environment variable to container ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

#If tag is not used, set VA_SERVING_TAG to default
if [ -z "$IMAGE" ]; then
  IMAGE=video-analytics-serving-$FRAMEWORK-tests:latest
fi

$WORK_DIR/../docker/run.sh --image $IMAGE  \
  -v $WORK_DIR:/home/video-analytics-serving/tests $DEV $CI $ENVIRONMENT $INTERACTIVE $ENTRYPOINT $ENTRYPOINT_ARGS
