#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

RELEASE_VERSION=0.24.0
SCRIPT_DIR=$(dirname $(readlink -f "$0"))

kubectl delete -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd/overlays/node-feature-rules?ref=v${RELEASE_VERSION}

# Start NFD - if your cluster doesn't have NFD installed yet
kubectl delete -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/nfd?ref=v${RELEASE_VERSION}

# Create GPU plugin daemonset
kubectl delete -f $SCRIPT_DIR/intel-gpu-plugin/intel-gpu-plugin.yaml
