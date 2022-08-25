#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
NAMESPACE=${NAMESPACE:-pipeline-server}

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

pkill -f check_for_changes.sh

launch microk8s kubectl delete serviceaccount,clusterrole,clusterrolebinding,configmap,daemonsets,services,deployments,pods --all --namespace=node-feature-discovery

launch microk8s kubectl delete configmap,daemonsets,services,deployments,pods --all

namespace_exists=$(microk8s kubectl get namespaces | grep $NAMESPACE)

if [ ! -z "$namespace_exists" ]; then
    launch microk8s kubectl delete namespaces $NAMESPACE
    launch microk8s kubectl config set-context --current --namespace=default
fi

echo "Stopped and removed all services"
