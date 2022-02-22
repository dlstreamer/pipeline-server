#!/bin/bash -e

# This assignment of CONSUMER_VERSION cascades (to override default 0.0.1) through build/deploy

WORK_DIR=$(dirname $(readlink -f "$0"))

MQTT_YAML=${WORK_DIR}/mqtt.yaml

echo "Deploying MQTT broker"
microk8s kubectl apply -f $MQTT_YAML

sleep 10

not_running=0
for (( i=0; i<25; ++i)); do
    not_running=$(microk8s kubectl get pods | grep "mqtt" | grep -vE 'Running' | wc -l)
    echo "Waiting for mqtt to start......."
    if [ $not_running == 0 ]; then
        echo "mqtt instance is up and running"
        break
    else
        sleep 10
    fi
done
if [ $not_running != 0 ]; then
    echo "Failed to deploy mqtt"
    exit 1
fi
