#!/bin/bash
set -e

TEST_DIR=$(dirname "$(readlink -f "$0")")
TAG=##teamcity
echo " ${TAG}[testSuiteStarted name='script-tests'] "

for TEST in $TEST_DIR/script_tests/* ; do
  TEST_NAME=$(basename $TEST)
  printf " %s[testStarted name='%s' captureStandardOutput='true']\n" "$TAG" "$TEST_NAME"
  TEST_DIR=$TEST_DIR $TEST || {
    printf " %s[testFailed name='%s']\n" "$TAG" "$TEST_NAME"
  }
  printf " %s[testFinished name='%s']\n" "$TAG" "$TEST_NAME"
done

echo " ${TAG}[testSuiteFinished name='script-tests'] "
