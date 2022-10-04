#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
TLS_PORT=8443

while [[ "$#" -gt 0 ]]; do
    case $1 in
            --tls-port)
                TLS_PORT=$2
                ;;
        esac
    shift
done

echo "Setup a bridged network for isolating HTTP endpoint"
docker network create -d bridge my_bridge

echo "Running NGINX web server in Bridged and host network"
docker run -itd --name=nginx -v ${SCRIPT_DIR}/cert/server.crt:/etc/ssl/certs/server.crt -v ${SCRIPT_DIR}/cert/server.key:/etc/ssl/certs/server.key -v ${SCRIPT_DIR}/nginx/nginx.conf:/etc/nginx/nginx.conf --network=my_bridge -p ${TLS_PORT}:443 nginx

echo "Running Pipeline Service with RTSP enabled and Web service disabled"
${SCRIPT_DIR}/../../docker/run.sh -v /tmp:/tmp --enable-rtsp --disable-http-port --network my_bridge
