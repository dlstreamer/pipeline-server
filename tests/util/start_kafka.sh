# Start simple Kafka broker 
echo "Launching zookeeper and kafka containers with auto-topic creation."
docker-compose -f docker-compose-kafka-vaserving.yml up -d
