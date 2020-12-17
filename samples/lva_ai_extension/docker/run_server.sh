#!/bin/bash

CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
IMAGE=video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension
NAME=${IMAGE//[\:]/_}
PORT=5001
PIPELINES=
ENTRYPOINT_ARGS=

function show_help {
  echo "usage: ./run_server.sh"
  echo "  [ -p : Specify the port to use ] "
  echo "  [ --pipeline-name : Specify the pipeline name to use ] "
  echo "  [ --pipeline-version : Specify the pipeline version to use ] "
  echo "  [ --debug : Use debug pipeline ] "
  echo "  [ --max-running-pipelines : Specify the maximum number of concurrent pipelines, default is 10 ] "
  echo "  [ --parameters : Specify a json string or file for pipeline parameters *Deprecated* ] "
  echo "  [ --pipeline-parameters : Specify a json string or file for pipeline parameters ] "
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

while [[ "$#" -gt 0 ]]; do
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
    --pipeline-name|--pipeline-version|--max-running-pipelines|--parameters|--pipeline-parameters)
      if [ "$2" ]; then
        ENTRYPOINT_ARGS+="--entrypoint-args $1 "
        ENTRYPOINT_ARGS+="--entrypoint-args $2 "
        shift
      else
        error "$1 expects a value"
      fi
      ;;
    --debug)
      ENTRYPOINT_ARGS+="--entrypoint-args $1 "
      ;;
    --dev)
      PIPELINES="--pipelines $LVA_DIR/pipelines "
      ;;
    *)
      ENTRYPOINT_ARGS+="--entrypoint-args $1 "
      ;;
  esac

  shift
done

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

if [ ! -z "$PARAMETERS" ]; then
  ENV+="-e PARAMETERS=$PARAMETERS "
fi

if [ ! -z "$PIPELINE_PARAMETERS" ]; then
  ENV+="-e PIPELINE_PARAMETERS=$PIPELINE_PARAMETERS "
fi

"$ROOT_DIR/docker/run.sh" --image $IMAGE -v /tmp:/tmp -v /dev/shm:/dev/shm -p $PORT:$PORT $ENTRYPOINT_ARGS $PIPELINES $ENV
