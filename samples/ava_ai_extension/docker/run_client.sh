#!/bin/bash

SERVER_IP=127.0.0.1
SERVER_PORT=5001
DOCKER_DIR=/home/edge-ai-extension
OUTPUT_FILE_PATH=/tmp/result
INTERACTIVE=
IMAGE=video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension
NAME=${IMAGE//[\:]/_}"_client"
NUMBER_OF_STREAMS=1
CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(dirname $CURRENT_DIR)
MODE=
VOLUME_MOUNT=
ENTRYPOINT_ARGS=
ENTRYPOINT="--entrypoint /bin/bash"
NETWORK="--network host"
RUN_COMMAND=
USER=

function run {
  if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $ROOT_DIR:$DOCKER_DIR "
  fi

  if [ ! -z "$VOLUME_MOUNT" ]; then
    USER="--user $UID"
  fi
  eval "docker run $INTERACTIVE --rm $VOLUME_MOUNT $NETWORK $ENTRYPOINT --name ${NAME} ${USER} $IMAGE -c $RUN_COMMAND"
}

function show_help {
  echo ""
  echo "**Run Script**"
  echo ""
  echo "usage: ./run_client.sh"
  echo "  [ -it : Run client in interactive mode ] "
  echo "  [ --output-file-path : Specify the output file path without extension to save inference results to (file must be inside container or in volume mounted path)] "
  echo "  [ --number-of-streams : Specify number of streams (one client process per stream)] "
  echo "  [ --dev : Mount local source code] "
  echo ""
  echo "**Application**"
  echo ""
  RUN_COMMAND="'python3 client --help'"
  run
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
    -it)
      INTERACTIVE="-it"
      ;;
    --output-file-path)
      if [ "$2" ]; then
        OUTPUT_FILE_PATH=$2
        shift
      else
        error "--output-file-path expects a value"
      fi
      ;;
    --number-of-streams)
      if [ "$2" ]; then
        NUMBER_OF_STREAMS=$2
        shift
      else
        error "--number-of-streams expects a value"
      fi
      ;;
    --dev)
        MODE=DEV
      ;;
    *)
      ENTRYPOINT_ARGS+=" '$1' "
      ;;
  esac

  shift
done

VOLUME_MOUNT+="-v /tmp:/tmp "
VOLUME_MOUNT+="-v /dev/shm:/dev/shm "
PIDS=
CONTAINERS=


function clean_up {
    kill -9 $PIDS
    docker kill $CONTAINERS
    exit
}


if [ "$NUMBER_OF_STREAMS" -gt "1" ]; then
    trap clean_up SIGHUP SIGINT SIGTERM
    for i in $(seq "$NUMBER_OF_STREAMS")
    do
      echo "Starting Client $i Results to ${OUTPUT_FILE_PATH}_client_$i.jsonl, Output to: client_${i}.stdout.txt"
      RUN_COMMAND='"'" python3 client $ENTRYPOINT_ARGS -o ${OUTPUT_FILE_PATH}_client_$i.jsonl "'"'
      run >client_${i}.stdout.txt 2>&1 &
      PIDS+=" $!"
      CONTAINERS+=" ${NAME}_${i}"
      sleep 1
    done
    echo "waiting for clients to finish"
    wait
else
    RUN_COMMAND='"'" python3 client $ENTRYPOINT_ARGS -o ${OUTPUT_FILE_PATH}.jsonl "'"'
    run
fi