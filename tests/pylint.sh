
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)

rm -rf pylint.results.json
python3 -m pylint ${SOURCE_DIR}/**/*.py --reports=y --output-format=json --score=y  --exit-zero >>pylint.results.json