#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
FRAMEWORK=gstreamer
RUN_PYLINT=false
DEV=

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
      --pylint)
        RUN_PYLINT=true
        ;;
      --dev)
        DEV=--dev
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
  echo "  [ --pylint : Set the flag to run the pylint test ] "
  echo "  [ --dev : Bash into the test container ] "
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

$WORK_DIR/../docker/run.sh --image $IMAGE \
 -v $WORK_DIR:/home/video-analytics-serving/tests $DEV

if [[ $RUN_PYLINT && -z $DEV ]] ; then
  $WORK_DIR/../docker/run.sh --image $IMAGE \
  -v $WORK_DIR:/home/video-analytics-serving/tests \
  --entrypoint ./tests/pylint.sh
fi
