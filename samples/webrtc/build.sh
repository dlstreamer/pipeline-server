#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$DOCKERFILE_DIR")

function show_help {
  echo "usage: ./build.sh"
  echo "  [ --remove-volumes ] Removes local volumes used to store information during previous session(s)."
  echo "  [ --help -h -? ] Usage information."
}

#Get options passed into script, passing through parameters supported by the parent build script.
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    *) # Default case: No more known options, so break out of the loop.
      PASS_THROUGH_PARAMS=$@
      break ;;
  esac
  shift
done

function launch { echo $@
    $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&20
        if [[ "$1" == *"grafana"* ]]; then
            echo "To re-build the \"grafana-storage\" volume used for sample Grafana dashboard, pass:"
            echo "--remove-volumes   (requires sudo)"
        fi 
        exit $exit_code
    fi
    return $exit_code
}

# Build Signaling Server container for simple WebRTC sample
echo $'\n\n=================================================='
echo "Building webrtc_signaling_server image..."
echo "$SOURCE_DIR/webrtc/signaling/build.sh"
echo "=================================================="
launch $SOURCE_DIR/webrtc/signaling/build.sh

# Build Web Server container to host WebRTC javascript sample
echo $'\n\n=================================================='
echo "Building webrtc_webserver image..."
echo "$SOURCE_DIR/webrtc/webserver/build.sh"
echo "=================================================="
launch $SOURCE_DIR/webrtc/webserver/build.sh

# Build Grafana container for MVP Dashboard using AJAX panels
echo $'\n\n=================================================='
echo "Building webrtc_grafana image..."
echo "$SOURCE_DIR/webrtc/grafana/build.sh"
echo "=================================================="
launch $SOURCE_DIR/webrtc/grafana/build.sh  $1

# Build Pipeline Server container
echo $'\n\n=================================================='
echo "Building Intel(R) DL Streamer Pipeline Server image..."
echo "$SOURCE_DIR/../docker/build.sh"
echo "=================================================="
launch $SOURCE_DIR/../docker/build.sh
