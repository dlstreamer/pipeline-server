#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))

proxy_config_exists=$(microk8s kubectl get configmap proxy-config)

if [ -z "$proxy_config_exists" ]; then
    PROXY_CONFIG=
    SPACE=" "
    PREFIX="--from-literal="

    if [ ! -z "$http_proxy" ]; then
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"http_proxy="${http_proxy}${SPACE}"
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"HTTP_PROXY="${http_proxy}${SPACE}"
    fi
    if [ ! -z "$https_proxy" ]; then
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"https_proxy="${https_proxy}${SPACE}"
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"HTTPS_PROXY="${https_proxy}${SPACE}"
    fi
    if [ ! -z "$no_proxy" ]; then
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"no_proxy="${no_proxy}${SPACE}"
        PROXY_CONFIG="${PROXY_CONFIG}${PREFIX}"NO_PROXY="${no_proxy}${SPACE}"
    fi

    echo "Creating proxy configmap with settings $PROXY_CONFIG"
    microk8s kubectl create configmap proxy-config "$PROXY_CONFIG"

fi
