# Launch simple MQTT broker
docker run -d --rm --name vaserving_mqtt -p 1883:1883 -p 9001:9001 eclipse-mosquitto
# Launch with broker configured to produce persistent output logs
#docker run --rm --name metapublish_mqtt -p 1883:1883 -p 9001:9001 -v mosquitto.conf:/mosquitto/mosquitto.conf -v /mosquitto/data -v /mosquitto/log eclipse-mosquitto &

# Install MQTT client
echo "Assuring MQTT client for pub/sub are installed"
sudo apt-get install -y mosquitto-clients

# Launch MQTT client listener, subscribing to default topic
echo "Listening for MQTT messages on 'vaserving' topic..."
mosquitto_sub -h localhost -t vaserving
mosquitto_pub -h localhost -p 1883 -t vaserving -m "MQTT message published from CI Build Agent."
# TODO: Output persistent broker logs (uncomment run comand above)
# or redirect console listener output 
