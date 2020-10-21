#!/bin/bash
IMAGE=video-analytics-serving-lva-ai-extension:latest
NAME=${IMAGE//[\:]/_}
docker run -it --rm -p 5001:5001 -v /dev/shm:/dev/shm --user openvino --name $NAME $IMAGE
