#!/bin/bash
ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)

RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/clamav"}
OUTPUT_FILE="$RESULTS_DIR/report.txt"
SCAN_DIR=${SCAN_DIR:-"/home"}

mkdir -p "$RESULTS_DIR"

freshclam

clamscan -r --bell -i ${SCAN_DIR} ${CLAMAV_ARGS} > ${OUTPUT_FILE}