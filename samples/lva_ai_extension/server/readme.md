To build and run the server

./build.sh

NOTE: At this time, build the main VA Serving Docker image with openvino base image before building this Dockerfile
./docker/build.sh --base openvino/ubuntu18_data_dev:2020.4

./run.sh

To communicate and test, use the lva client that is available
