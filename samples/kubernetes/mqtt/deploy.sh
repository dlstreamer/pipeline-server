#!/bin/bash -e

# This assignment of CONSUMER_VERSION cascades (to override default 0.0.1) through build/deploy

WORK_DIR=$(dirname $(readlink -f "$0"))

MQTT_YAML=${WORK_DIR}/mqtt.yaml

echo "Deploying mosquitto broker"
microk8s kubectl apply -f $MQTT_YAML

sleep 10