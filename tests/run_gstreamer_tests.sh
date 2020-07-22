#!/bin/bash
WORK_DIR=$(dirname $(readlink -f "$0"))
RUN_ON_HOST=false

function show_help {
  echo "usage: run_gstreamer_tests.sh"
  echo "  [ --run-on-host : Run test on host instead of a container ]"
}

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --run-on-host)
        RUN_ON_HOST=true
        ;;
      *)
        break
        ;;
    esac

    shift
  done
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

echo "Running VA Serving Functional Tests (GStreamer)"

if $RUN_ON_HOST; then
  #Run test on host
  export FRAMEWORK=gstreamer
  pytest $WORK_DIR/..
else
  #Run test in container
  if [[ "$(docker images -q video-analytics-serving-gstreamer-tests:latest 2> /dev/null)" == "" ]]; then
    # do something
    echo "error, test image does not exist. Please build gstreamer test image"
  else
    #Container should already have FRAMEWORK set
    $WORK_DIR/../docker/run.sh --image video-analytics-serving-gstreamer-tests:latest \
    -v $WORK_DIR:/home/video-analytics-serving/tests \
    --entrypoint pytest
  fi
fi
