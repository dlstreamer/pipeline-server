# Start simple Kafka broker 
# We needed to slightly modify from this original Bitnami source
#curl -sSL https://raw.githubusercontent.com/bitnami/bitnami-docker-kafka/master/docker-compose.yml > docker-compose-kafka.yml
cp docker-compose-kafka-VAS.yml docker-compose-kafka.yml
echo "Launching zookeeper and kafka containers with auto-topic creation on a distinct network."
docker-compose -f docker-compose-kafka.yml up -d
