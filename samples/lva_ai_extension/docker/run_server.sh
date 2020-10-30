#!/bin/bash

IMAGE=video-analytics-serving-lva-ai-extension:latest
NAME=${IMAGE//[\:]/_}
PORT=5001

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      -p)
        if [ "$2" ]; then
          PORT=$2
          shift
        else
          error "-p expects a value"
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
  echo "usage: ./run_server.sh"
  echo "  [ -p : Specify the port to use ] "
  echo "  [ --pipeline-name : Specify the pipeline name to use ] "
  echo "  [ --pipeline-version : Specify the pipeline version to use ] "
  echo "  [ --debug : Use debug pipeline ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"

ENV=

if [ ! -z "$PIPELINE_NAME" ]; then
  ENV+="-e PIPELINE_NAME=$PIPELINE_NAME "
fi

if [ ! -z "$PIPELINE_VERSION" ]; then
  ENV+="-e PIPELINE_VERSION=$PIPELINE_VERSION "
fi

if [ ! -z "$DEBUG_PIPELINE" ]; then
  ENV+="-e DEBUG_PIPELINE=$DEBUG_PIPELINE "
fi

docker run -it --rm $ENV -p $PORT:$PORT -v /dev/shm:/dev/shm -v /tmp:/tmp --user openvino --name $NAME $IMAGE $@
