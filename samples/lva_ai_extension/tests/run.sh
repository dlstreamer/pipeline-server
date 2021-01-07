IMAGE=video-analytics-serving-lva-tests
CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
docker stop $IMAGE
LOCAL_RESULTS_DIR="$CURRENT_DIR/results"
DOCKER_RESULTS_DIR="/home/video-analytics-serving/samples/lva_ai_extension/tests/results"
mkdir -p "$LOCAL_RESULTS_DIR"
RESULTS_VOLUME_MOUNT="-v $LOCAL_RESULTS_DIR:$DOCKER_RESULTS_DIR "
"$ROOT_DIR/docker/run.sh" --image $IMAGE -v /dev/shm:/dev/shm $RESULTS_VOLUME_MOUNT --pipelines "$LVA_DIR/pipelines" -p 5001:5001 --user $UID "$@"
