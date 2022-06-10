#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SAMPLES_DIR=$(dirname $SCRIPT_DIR)
ROOT_DIR=$(dirname $SAMPLES_DIR)

PIPELINE=object_detection/record_frames
MEDIA=https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
BROKER_ADDR=localhost
BROKER_PORT=1883
TOPIC=pipeline-server
SPECIFIER="%08d"

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --frame-store)
      if [ "$2" ]; then
        FRAME_STORE=$(readlink -f "$2")
        shift
      else
        echo "--frame-store expects a value"
        exit 1
      fi
      ;;
    *)
      ;;
  esac

  shift
done

if [ -z $FRAME_STORE ]; then
   echo Frame store path not specified
   exit 1
fi

FILE_LOCATION=$FRAME_STORE/$SPECIFIER.jpg
$ROOT_DIR/client/pipeline_client.sh start $PIPELINE $MEDIA \
   --destination type mqtt --destination host $BROKER_ADDR:$BROKER_PORT --destination topic $TOPIC \
   --parameter file-location $FILE_LOCATION
echo Frame store file location = $FILE_LOCATION
echo Starting mqtt client
python3 $SCRIPT_DIR/mqtt_client.py --broker-address $BROKER_ADDR --broker-port $BROKER_PORT --topic $TOPIC --frame-store-template $FILE_LOCATION
