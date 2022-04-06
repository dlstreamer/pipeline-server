#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
ADD_PROXY_ENV=${ADD_PROXY_ENV:-true}
CPU_DEVICE_DEPLOYMENT_DIR="${WORK_DIR}/deployments/cpu"
GPU_DEVICE_DEPLOYMENT_DIR="${WORK_DIR}/deployments/gpu"

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

echo "Deploying Intel GPU device plugin "
launch microk8s kubectl apply -k https://github.com/kubernetes-sigs/node-feature-discovery/deployment/overlays/default?ref=v0.10.1
launch microk8s kubectl apply -k https://github.com/intel/intel-device-plugins-for-kubernetes/deployments/gpu_plugin/overlays/nfd_labeled_nodes?ref=v0.23.0
sleep 10
running=0
for (( i=0; i<25; ++i)); do
    running=$(microk8s kubectl get pods | grep "intel-gpu-plugin" | grep -E 'Running' | wc -l)
    echo "Waiting for Intel GPU plugin to start......."
    if [ $running == 0 ]; then
        sleep 10
    else
        echo "Intel GPU plugin enabled"
        break
    fi
done

echo "Deploying Pipeline Server CPU worker"
launch microk8s kubectl apply -k $CPU_DEVICE_DEPLOYMENT_DIR

echo "Deploying Pipeline Server GPU worker"
launch microk8s kubectl apply -k $GPU_DEVICE_DEPLOYMENT_DIR

sleep 10

not_running=0
for (( i=0; i<25; ++i)); do
    not_running=$(microk8s kubectl get pods | grep "pipeline-server.*worker" | grep -vE 'Running' | wc -l)
    echo "Waiting for Pipeline Server instances to start......."
    if [ $not_running == 0 ]; then
        echo "All Pipeline Server instances are up and running"
        break
    else
        sleep 10
    fi
done
if [ $not_running != 0 ]; then
    echo "Failed to deploy Pipeline Server, not all Services are in running state"
    exit 1
fi

echo "$(microk8s kubectl get pods)"
