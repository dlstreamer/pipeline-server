#!/bin/bash

SERVER_IP=127.0.0.1
SERVER_PORT=5001
LVA_ROOT=/home/video-analytics-serving/samples/lva_ai_extension
SAMPLE_FILE_PATH=$LVA_ROOT/sampleframes/sample01.png
OUTPUT_FILE_PATH=/tmp/result
SHARED_MEMORY=
INTERACTIVE=
IMAGE=video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension
NUMBER_OF_STREAMS=1
SCRIPT_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $SCRIPT_DIR)
MODE=
VOLUME_MOUNT=
ENTRYPOINT_ARGS=

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
  if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $SAMPLE_DIR:$LVA_ROOT "
  fi

  docker run --rm $VOLUME_MOUNT --entrypoint /bin/bash $IMAGE -c "python3 ${LVA_ROOT}/client --help"
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
      ENTRYPOINT_ARGS+=" $1 "
      ;;
  esac

  shift
done

VOLUME_MOUNT+="-v /tmp:/tmp "
VOLUME_MOUNT+="-v /dev/shm:/dev/shm "
PIDS=
CONTAINERS=

if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $SAMPLE_DIR:$LVA_ROOT "
fi

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
	RUN_COMMAND="python3 $LVA_ROOT/client $ENTRYPOINT_ARGS -o ${OUTPUT_FILE_PATH}_client_$i.jsonl "
	docker run $INTERACTIVE --name lva_ai_extension_client_$i --rm --network=host $VOLUME_MOUNT --user "$UID" --entrypoint /bin/bash $IMAGE -c "$RUN_COMMAND" >client_${i}.stdout.txt 2>&1 &
	PIDS+=" $!"
	CONTAINERS+=" lva_ai_extension_client_${i}"
	sleep 1
    done
    echo "waiting for clients to finish"
    wait
else
    RUN_COMMAND="python3 $LVA_ROOT/client $ENTRYPOINT_ARGS -o ${OUTPUT_FILE_PATH}.jsonl $@"
    docker run $INTERACTIVE --rm --network=host $VOLUME_MOUNT --user "$UID" --entrypoint /bin/bash $IMAGE -c "$RUN_COMMAND"
fi
