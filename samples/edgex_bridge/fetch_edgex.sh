#!/bin/bash
# This script builds a docker-compose file for EdgeX
# and fetches a configuration template for device-mqtt-go.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PS_SOURCE=$SCRIPT_DIR/../..
EDGEX_PROJECT=$SCRIPT_DIR/edgex
mkdir -p $EDGEX_PROJECT
cd $EDGEX_PROJECT
echo "Working folder: $PWD"

# Fetch config template from published EdgeX device-mqtt-go docker image.
CONFIG_TARGET=$EDGEX_PROJECT/res/device-mqtt-go
mkdir -p $CONFIG_TARGET
docker create --rm --name dev_mqtt \
    -v $CONFIG_TARGET:/tmp \
    edgexfoundry/docker-device-mqtt-go:1.3.1 \
    /bin/sh
docker cp dev_mqtt:/res/configuration.toml $EDGEX_PROJECT/res/device-mqtt-go/configuration.toml.edgex
docker rm -f dev_mqtt

# Fetch EdgeX launch instructions
EDGEX_DIR_REPO_DEVELOPER_SCRIPTS="$EDGEX_PROJECT/edgex-compose/"
EDGEX_VERSION_TAG="hanoi"
if ! rm -Rf "$EDGEX_DIR_REPO_DEVELOPER_SCRIPTS"; then
    echo "ERROR removing existing $EDGEX_DIR_REPO_DEVELOPER_SCRIPTS folder!"
    exit $?
fi

if ! git clone -b $EDGEX_VERSION_TAG https://github.com/edgexfoundry/edgex-compose.git $EDGEX_DIR_REPO_DEVELOPER_SCRIPTS; then
    echo "ERROR cloning EdgeX repository!"
    exit $?
fi

# TODO: Add ds-camera
cd "${EDGEX_DIR_REPO_DEVELOPER_SCRIPTS}compose-builder/"
if ! make compose no-secty mqtt-broker ds-mqtt mqtt-bus ; then
    echo "ERROR making EdgeX compose file!"
    exit $?
fi

if [ ! -f "${EDGEX_DIR_REPO_DEVELOPER_SCRIPTS}/docker-compose-hanoi-no-secty-mqtt.yml" ] ; then
    echo "Generated compose file not found in expected output location!"
    exit $?
fi

if ! cp "${EDGEX_DIR_REPO_DEVELOPER_SCRIPTS}/docker-compose-hanoi-no-secty-mqtt.yml" "$EDGEX_PROJECT/docker-compose.yml" ; then
    echo "ERROR copying generated EdgeX compose file!"
    exit $?
fi
echo "Successfully fetched repo and produced compose file."
cd $PS_SOURCE
