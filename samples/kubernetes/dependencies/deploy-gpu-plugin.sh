#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

RELEASE_VERSION=0.24.0
SCRIPT_DIR=$(dirname $(readlink -f "$0"))
NUM_OF_SHARED_DEVICE=${1:-2}
sed -i "s/shared-dev-num=.*\"/shared-dev-num=$NUM_OF_SHARED_DEVICE\"/" $SCRIPT_DIR/intel-gpu-plugin/intel-gpu-plugin.yaml

# Start NFD - if your cluster doesn't have NFD installed yet
kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=v${RELEASE_VERSION}

# Create NodeFeatureRules for detecting GPUs on nodes
kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=v${RELEASE_VERSION}

# Create GPU plugin daemonset
kubectl apply -f $SCRIPT_DIR/intel-gpu-plugin/intel-gpu-plugin.yaml
