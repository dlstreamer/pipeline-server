VAS_TOPIC=$1
#Launch MQTT broker
#docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto &
#Launch client listener, subscribing to default topic
echo "Listening for MQTT messages on '${VAS_TOPIC}' topic..."
mosquitto_sub -h localhost -t ${VAS_TOPIC}

