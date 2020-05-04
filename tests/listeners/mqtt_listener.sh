# Launch simple MQTT broker
docker run -d --rm --name vaserving_mqtt -p 1883:1883 -p 9001:9001 eclipse-mosquitto
# Launch with configured persistence to output log
#docker run --rm --name metapublish_mqtt -p 1883:1883 -p 9001:9001 -v mosquitto.conf:/mosquitto/mosquitto.conf -v /mosquitto/data -v /mosquitto/log eclipse-mosquitto &

# Launch client listener, subscribing to default topic
echo "Listening for MQTT messages on 'vaserving' topic..."
mosquitto_sub -h localhost -t vaserving

# TODO: Output persistent logs similar to above, 
# or redirect console output 