#!/bin/bash -e

# Building Video Analytics Serving as a base image. GStreamer integration example.
VIDEO_ANALYTICS_SERVING_REPO="https://github.intel.com/intel/video-analytics-serving.git"
sudo docker build ${VIDEO_ANALYTICS_SERVING_REPO} --file Dockerfile.gst -t "video_analytics_serving_gstreamer_base:latest" $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /')

# Next integrate your service/application to be deployed and run alongside Video Analytics Serving components.
# To build your docker file, check "SampleIntegrationDockerfile"
sudo docker build -t "video_analytics_serving_gstreamer:latest" $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /') .
