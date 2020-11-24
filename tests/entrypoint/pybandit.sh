#!/bin/bash
ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)
SCAN_DIR=${SCAN_DIR:-$SOURCE_DIR}
RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/pybandit"}
OUTPUT_FILE="$RESULTS_DIR/pybandit_report.html"
OUTPUT_FORMAT=${OUTPUT_FORMAT:-html}

bandit --version

mkdir -p "$RESULTS_DIR"

echo "Command: bandit -r $SOURCE_DIR -o $OUTPUT_FILE -f $OUTPUT_FORMAT -v -n 5 -ll"
bandit -r $SOURCE_DIR -o $OUTPUT_FILE -f $OUTPUT_FORMAT -v -n 5 -ll

