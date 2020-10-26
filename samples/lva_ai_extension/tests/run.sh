CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
docker stop video-analytics-serving-lva-tests
"$ROOT_DIR/docker/run.sh" --image video-analytics-serving-lva-tests -v /dev/shm:/dev/shm --pipelines "$LVA_DIR/pipelines" "$@"
