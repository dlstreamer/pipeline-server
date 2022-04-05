#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Usage:
# ./start_pipeline_psclient.sh  [--remote]
#
# --remote   Print out the URL to paste into remote browser.
#
# Default behavior attempts to automatically launch browser with the WebRTC viewing URL.

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$SCRIPT_DIR")
PIPELINE_SERVER=http://localhost:8080
PIPELINE="object_detection/person_vehicle_bike"
VIDEO_INPUT2="https://github.com/intel-iot-devkit/sample-videos/blob/master/face-demographics-walking-and-pause.mp4?raw=true"

# Prepare unique peer-id for WebRTC connection to frame destination
RANDOM=$(date +%s%N | cut -b10-19)
PEER_ID="pipeline_webrtc1_${RANDOM}"

$SOURCE_DIR/../../client/pipeline_client.sh --quiet start \
   --server-address $PIPELINE_SERVER \
   $PIPELINE \
   $VIDEO_INPUT2 \
   --webrtc-peer-id $PEER_ID --show-request

# Start Pipeline Server pipeline using Pipeline Server client to initiate request.
instance_id="$($SOURCE_DIR/../../client/pipeline_client.sh --quiet start \
   --server-address $PIPELINE_SERVER \
   $PIPELINE \
   $VIDEO_INPUT2 \
   --webrtc-peer-id $PEER_ID | tail -n 1)"
echo $instance_id
echo "launched with PeerID=${PEER_ID}"

# Launch browser with query parameters to auto-connect to frame destination
pushd $SCRIPT_DIR
./launch_browser.sh $PEER_ID $instance_id $1
popd
