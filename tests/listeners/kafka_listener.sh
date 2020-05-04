echo "Fetching docker-compose-kafka.yml"
# We needed to slightly modify from this original Bitnami source
#curl -sSL https://raw.githubusercontent.com/bitnami/bitnami-docker-kafka/master/docker-compose.yml > docker-compose-kafka.yml
cp docker-compose-kafka-VAS.yml docker-compose-kafka.yml
echo "Launching zookeeper and kafka containers with auto-topic creation on a distinct network."
docker-compose -f docker-compose-kafka.yml up -d
echo "Listening for Kafka messages on 'vaserving' topic..."
docker exec -it vaserving_kafka_1 /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic vaserving
#TODO: Output console without timestamps to file for comparison
#      Or configure Kafka to log output. Whichever is easiest