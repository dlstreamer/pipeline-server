#!/bin/bash

ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)
AVA_DIR=$(readlink -f "$SOURCE_DIR/..")

RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results"}
PYTEST_ARGS=${PYTEST_ARGS:-"$@"}

mkdir -p "$RESULTS_DIR"

COV_DIR="$RESULTS_DIR/coverage"
CACHE_DIR="$RESULTS_DIR/cache"

rm -rf "$COV_DIR"
rm -rf "$CACHE_DIR"

cd ${SOURCE_DIR};

pytest -s --html="$RESULTS_DIR/report.html" --self-contained-html \
  --cov-report=html:"$COV_DIR" --cov="$AVA_DIR" $PYTEST_ARGS -o cache_dir=$CACHE_DIR

TEST_RESULT=$?

coverage report

rm -rf "$RESULTS_DIR/.coverage"
rm -rf "$CACHE_DIR"

exit $TEST_RESULT
