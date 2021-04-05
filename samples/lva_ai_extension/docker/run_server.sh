#!/bin/bash

CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
LVA_ROOT=/home/video-analytics-serving/samples/lva_ai_extension
IMAGE=video-analytics-serving:0.5.0-dlstreamer-edge-ai-extension
VASERVING_ROOT=/home/video-analytics-serving
NAME=${IMAGE//[\:]/_}
PORT=5001
PIPELINES=
ENTRYPOINT_ARGS=
MODE=
VOLUME_MOUNT=
RTSP_ARGS=

function show_help {
  echo ""
  echo "**Run Script**"
  echo ""
  echo "usage: ./run_server.sh"
  echo "  [ -p : Specify the port to use ] "
  echo "  [ --dev : Mount local source code] "
  echo ""
  echo "**Application**"
  echo ""
  if [ "${MODE}" == "DEV" ]; then
      VOLUME_MOUNT+="-v $LVA_DIR:$LVA_ROOT "
      VOLUME_MOUNT+="-v $ROOT_DIR:$VASERVING_ROOT "
      PIPELINES="--pipelines $LVA_DIR/pipelines "
  fi
  ENTRYPOINT_ARGS+="--entrypoint-args --help "  
  "$ROOT_DIR/docker/run.sh" -p $PORT:$PORT --image $IMAGE $VOLUME_MOUNT $ENTRYPOINT_ARGS $PIPELINES 
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
    --dev)
	PIPELINES="--pipelines $LVA_DIR/pipelines "
	MODE="DEV"
      ;;
    *)
      ENTRYPOINT_ARGS+="--entrypoint-args '$1' "
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

if [ ! -z "$ENABLE_RTSP" ]; then
  RTSP_ARGS="--enable-rtsp"
fi

if [ ! -z "$GST_DEBUG" ]; then
  ENV+="-e GST_DEBUG=$GST_DEBUG "
fi

VOLUME_MOUNT+="-v /tmp:/tmp "
VOLUME_MOUNT+="-v /dev/shm:/dev/shm "

if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $LVA_DIR:$LVA_ROOT "
    VOLUME_MOUNT+="-v $ROOT_DIR:$VASERVING_ROOT "
fi

"$ROOT_DIR/docker/run.sh" --image $IMAGE $VOLUME_MOUNT -p $PORT:$PORT $RTSP_ARGS $ENTRYPOINT_ARGS $PIPELINES $ENV
