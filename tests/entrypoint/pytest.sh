#!/bin/bash

ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)
FRAMEWORK=${FRAMEWORK:-gstreamer}

RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/pytest/$FRAMEWORK"}

mkdir -p "$RESULTS_DIR"

COV_CONFIG="$TESTS_DIR/config/coveragerc_${FRAMEWORK}"
COV_DIR="$RESULTS_DIR/coverage"

rm -rf "$COV_DIR"

cd ${SOURCE_DIR};
python3 -m pytest -s --html="$RESULTS_DIR/report.html" --ignore=$SOURCE_DIR/samples --self-contained-html \
  --cov-report=html:"$COV_DIR" --cov-config=$COV_CONFIG --cov=vaserving ${PYTEST_ARGS}
