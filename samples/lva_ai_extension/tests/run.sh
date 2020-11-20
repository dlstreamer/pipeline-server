IMAGE=video-analytics-serving-lva-tests
CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$CURRENT_DIR/../../..")
LVA_DIR=$(dirname $CURRENT_DIR)
docker stop $IMAGE
"$ROOT_DIR/docker/run.sh" --image $IMAGE -v /dev/shm:/dev/shm --pipelines "$LVA_DIR/pipelines" -p 5001:5001 --user $UID "$@"
