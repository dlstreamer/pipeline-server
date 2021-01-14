#!/bin/bash
set -e

TEST_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $TEST_DIR)
TAG=##teamcity
echo " ${TAG}[testSuiteStarted name='script-tests'] "


error() {

    # Return an error message from test script
    # OUTPUT and RETURN_CODE are taken from environment
    
    echo "======================="
    echo "Test Failed"
    echo "Return Code: $RETURN_CODE"
    echo "Detail: $1"
    echo "======================="
    echo "Output Begin"
    echo "======================="
    echo "$OUTPUT"
    echo "======================="
    echo "Output End"
    echo "======================="
    exit 1
}

# export function for use in test scripts
typeset -fx error 

run_test() {
  TEST_NAME=$(basename $1)
  printf " %s[testStarted name='%s' captureStandardOutput='true']\n" "$TAG" "$TEST_NAME"
  (TEST_DIR=$TEST_DIR SOURCE_DIR=$SOURCE_DIR $1) || {
    printf " %s[testFailed name='%s']\n" "$TAG" "$TEST_NAME"
  }
  printf " %s[testFinished name='%s']\n" "$TAG" "$TEST_NAME"    
}

if [ ! -z "$1" ]; then
    TEST=$TEST_DIR/script_tests/$(basename $1)
    run_test $TEST
else
    for TEST in $TEST_DIR/script_tests/* ; do
	run_test $TEST
    done
fi

echo " ${TAG}[testSuiteFinished name='script-tests'] "
