#!/bin/bash
TARGET_IMAGE=${IMAGE:-video-analytics-serving-gstreamer:latest}
TESTS_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $TESTS_DIR)
RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/dockerbench"}
OUTPUT_DIR="/usr/local/bin/results"
OUTPUT_NAME=${OUTPUT_NAME:-"docker.benchmark.results.txt"}
OUTPUT_FILE="$OUTPUT_DIR/$OUTPUT_NAME"

echo "Sending output to: $RESULTS_DIR/$OUTPUT_NAME"
mkdir -p "$RESULTS_DIR"

#INTERACTIVE_MODE="-it --entrypoint /bin/sh"
docker_bench_args="-t $TARGET_IMAGE -l $OUTPUT_FILE"

docker run $INTERACTIVE --net host --pid host --userns host \
   --cap-add audit_control \
   -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
   -e TARGET_IMAGE=$TARGET_IMAGE \
   -v /etc:/etc:ro \
   -v /lib/systemd/system:/lib/systemd/system:ro \
   -v /usr/bin/containerd:/usr/bin/containerd:ro \
   -v /usr/bin/runc:/usr/bin/runc:ro \
   -v /usr/lib/systemd:/usr/lib/systemd:ro \
   -v /var/lib:/var/lib:ro \
   -v /var/run/docker.sock:/var/run/docker.sock:ro \
   -v $RESULTS_DIR:$OUTPUT_DIR:rw \
   --label docker_bench_security \
docker/docker-bench-security $docker_bench_args
