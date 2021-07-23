#!/bin/bash
IMAGE=video-analytics-serving-lva-tests
CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
TESTS_DIR="$LVA_DIR/tests"
docker stop $IMAGE
LOCAL_RESULTS_DIR="$CURRENT_DIR/results"
DOCKER_RESULTS_DIR="/home/video-analytics-serving/samples/lva_ai_extension/tests/results"
mkdir -p "$LOCAL_RESULTS_DIR"
RESULTS_VOLUME_MOUNT="-v $LOCAL_RESULTS_DIR:$DOCKER_RESULTS_DIR "
PREPARE_LVA_GROUND_TRUTH=false
ENTRYPOINT_ARGS=

function show_help {
  echo "usage: run.sh (options are exclusive)"
  echo "  [ --pytest-lva-generate : Generate new LVA ground truth ]"
}

ARGS=$@
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    --pytest-lva-generate)
      ENTRYPOINT_ARGS+="--entrypoint-args --generate "
      VOLUME_MOUNT+="-v $TESTS_DIR/test_cases:$DOCKER_TESTS_DIR/test_cases "
      PREPARE_LVA_GROUND_TRUTH=true
      ;;
    *)
      break
      ;;
  esac
  shift
done

"$ROOT_DIR/docker/run.sh" --image $IMAGE -v /dev/shm:/dev/shm \
  -v "$LVA_DIR/tests/test_cases:/home/video-analytics-serving/samples/lva_ai_extension/tests/test_cases" \
  $RESULTS_VOLUME_MOUNT --pipelines "$LVA_DIR/pipelines" -p 5001:5001 \
  $ENTRYPOINT_ARGS "$@"

if [ $PREPARE_LVA_GROUND_TRUTH == true ]; then
  echo "Renaming .json.generated files to .json in preparation to update ground truth."
  find $TESTS_DIR/test_cases -depth -name "*.json.generated" -exec sh -c 'mv "$1" "${1%.json.generated}.json"' _ {} \;
fi