# This script invokes docker-compose to launch EdgeX microservices.
# You must have already successfully run ./fetch_edgex.sh AND
# the sample/edgex_bridge/edgex_bridge.py script with --generate flag
# before running start_edgex.sh.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
COMPOSE_PATH=$SCRIPT_DIR/../../edgex
COMPOSE_FILE=$COMPOSE_PATH/docker-compose.override.yml

if test -f "$COMPOSE_FILE"; then
    echo "Fetch_Edgex and EdgeX_Bridge --generate have completed."
    cd $COMPOSE_PATH
    docker-compose up -d
    # EdgeX microservices generally start up within 15s
    sleep 15
    # Next steps:
    # 1. Confirm device-mqtt is registered and running
    # "curl -i --get http://localhost:48081/api/v1/deviceservice/name/edgex-device-mqtt"
    # 2. Confirm our designated device profile is registered with EdgeX:"
    # "curl -i --get http://localhost:48081/api/v1/device/name/videoAnalytics-mqtt"
    # 3. Run a VA Serving pipeline that uses EdgeX extension.
    # Then confirm Events are received on the designated device profile"
    # "curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/100"
else
    echo "ERROR! You must first successfully run ./fetch_edgex.sh and edgex_bridge.py --generate"
fi
