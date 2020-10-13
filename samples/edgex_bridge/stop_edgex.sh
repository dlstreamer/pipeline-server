SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $SCRIPT_DIR/../../edgex
docker-compose down

echo "NOTE: EdgeX data still persists in docker volumes."
