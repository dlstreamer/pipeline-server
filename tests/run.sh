#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
FRAMEWORK=gstreamer
SUFFIX=latest
RUN_PYLINT=true

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
      --suffix)
        if [ "$2" ]; then
          SUFFIX=$2
          shift
        else
          error "Suffix expects a value"
        fi
        ;;
      --pylint)
        RUN_PYLINT=true
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
  echo "  [ --suffix : ]"
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

$WORK_DIR/../docker/run.sh --image video-analytics-serving-$FRAMEWORK-tests:$SUFFIX \
 -v $WORK_DIR:/home/video-analytics-serving/tests \

if $RUN_PYLINT; then
  $WORK_DIR/../docker/run.sh --image video-analytics-serving-$FRAMEWORK-tests:$SUFFIX \
  -v $WORK_DIR:/home/video-analytics-serving/tests \
  --entrypoint ./tests/pylint.sh
fi
