#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

# Usage:
# ./launch_browser.sh <instance_id>  [--remote]
# 
#    <instance_id> is a UUID value returned by Pipeline Server after pipeline is instantiated.
#
#    --remote   Print out the URL to paste into remote browser.
#
# Default behavior attempts to automatically launch browser with the WebRTC viewing URL.

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$DOCKERFILE_DIR")

# This currently launches default browser on a localhost system running Ubuntu.
WEB_SERVER=http://localhost:8082
# IMPORTANT: Update the value of WEB_SERVER variable as appropriate for your deployment model.
#            For example, to refer to a remote host/cluster.
# WEB_SERVER=http://${HOSTNAME}.internal.acme.com:8082
# WEB_SERVER=https://acme.com
peer_id=$1
instance_id=$2
url_full="${WEB_SERVER}?destination_peer_id=$peer_id&instance_id=${instance_id}"
if [ "$3" == "--remote" ]; then
   echo "In your remote browser, paste the following and press ENTER"
   echo $url_full
else
   xdg-open $url_full
fi
