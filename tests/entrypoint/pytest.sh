#!/bin/bash

ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)
FRAMEWORK=${FRAMEWORK:-gstreamer}

RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/pytest/$FRAMEWORK"}
PYTEST_ARGS=${PYTEST_ARGS:-"$@"}

mkdir -p "$RESULTS_DIR"

COV_CONFIG="$TESTS_DIR/config/coveragerc_${FRAMEWORK}"
COV_DIR="$RESULTS_DIR/coverage"
CACHE_DIR="$RESULTS_DIR/cache"

rm -rf "$COV_DIR"
rm -rf "$CACHE_DIR"

cd ${SOURCE_DIR};
python3 -m pytest -s --html="$RESULTS_DIR/report.html" --ignore=$SOURCE_DIR/samples --self-contained-html \
  --cov-report=html:"$COV_DIR" --cov-config=$COV_CONFIG --cov=server $PYTEST_ARGS -o cache_dir=$CACHE_DIR
exit_code=$?
if [[ $exit_code -ne 0 ]]; then
  echo "Tests failed, non zero exit code $exit_code"
fi
if [[ $exit_code -eq 139 ]]; then
  echo "Segmentation fault"
fi
exit $exit_code
