SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)

cd ${SOURCE_DIR}; python3 -m pytest -s