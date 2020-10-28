# This script builds a docker-compose file for EdgeX
# and fetches a configuration template for device-mqtt-go.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VAS_SOURCE=$SCRIPT_DIR/../..
cd $VAS_SOURCE/edgex
echo "Working folder: $PWD"

# Fetch config template from published EdgeX device-mqtt-go docker image.
CONFIG_TARGET=$VAS_SOURCE/edgex/res/device-mqtt-go
mkdir -p $CONFIG_TARGET
docker create --rm --name dev_mqtt \
    -v $CONFIG_TARGET:/tmp \
    nexus3.edgexfoundry.org:10004/docker-device-mqtt-go:master \
    /bin/sh
docker cp dev_mqtt:/res/configuration.toml $VAS_SOURCE/edgex/res/device-mqtt-go/configuration.toml.edgex
docker rm -f dev_mqtt

# Fetch EdgeX launch instructions
cd $VAS_SOURCE/edgex
git clone https://github.com/edgexfoundry/developer-scripts.git
cd ./developer-scripts/releases/nightly-build/compose-files/source
make compose no-secty mqtt
cp ../docker-compose-nexus-no-secty-mqtt.yml $VAS_SOURCE/edgex/docker-compose.yml
cd $VAS_SOURCE

echo "Next steps:"
echo ./docker/build.sh
echo ./docker/run.sh --dev
echo python3 samples/edgex_bridge/edgex_bridge.py --topic object_events --generate
echo "docker-compose up -d"
echo python3 samples/edgex_bridge/edgex_bridge.py --topic object_events
