#!/bin/bash
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)

# Example:
# ./pytest.sh --framework ffmpeg -k valid_pipeline_ffmpeg -vv

PYTEST_PARAMS="$@"
cd ${SOURCE_DIR}; python3 -m pytest -s --cov=vaserving $PYTEST_PARAMS
