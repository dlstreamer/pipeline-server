#!/bin/bash
ENTRYPOINT_DIR=$(dirname "$(readlink -f "$0")")
TESTS_DIR=$(dirname $ENTRYPOINT_DIR)
SOURCE_DIR=$(dirname $TESTS_DIR)

RESULTS_DIR=${RESULTS_DIR:-"$TESTS_DIR/results/pylint"}
OUTPUT_FILE="$RESULTS_DIR/report.txt"
OUTPUT_FORMAT=${OUTPUT_FORMAT:-text}
PYLINT_RC_FILE_PATH=${PYLINT_RC_FILE_PATH:-"$TESTS_DIR/config/.pylintrc"}
PYLINT_ARGS=${PYLINT_ARGS:-"$@"}

pylint --version

mkdir -p "$RESULTS_DIR"

# Enable Recursion into Subdirectories
shopt -s globstar
echo "Processing source files in $SOURCE_DIR. Results will output to: $OUTPUT_FILE"
cd ${SOURCE_DIR};
python3 -m pylint ${SOURCE_DIR}/**/*.py --reports=y --rcfile="$PYLINT_RC_FILE_PATH" \
   --output-format=$OUTPUT_FORMAT --score=y --exit-zero $PYLINT_ARGS > $OUTPUT_FILE
shopt -u globstar
