#!/bin/bash
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)
OUTPUT_FILE=${1:-pylint.results.txt}
OUTPUT_FORMAT=${2:-text}
pylint --version

# Enable Recursion into Subdirectories
shopt -s globstar
rm -rf $SOURCE_DIR/tests/$OUTPUT_FILE
echo "Processing source files in $SOURCE_DIR. Results will output to: $SOURCE_DIR/tests/$OUTPUT_FILE"
python3 -m pylint ${SOURCE_DIR}/**/*.py --reports=y --output-format=$OUTPUT_FORMAT --score=y --exit-zero >> $SOURCE_DIR/tests/$OUTPUT_FILE
shopt -u globstar
