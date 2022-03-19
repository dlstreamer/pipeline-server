#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
NAMESPACE=${NAMESPACE:-pipeline-server}
PIPELINE_SERVER_WORKER_DIR="$WORK_DIR/pipeline-server-worker"
RUN_HAPROXY_BACKGROUND=${RUN_HAPROXY_BACKGROUND:-true}

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

$WORK_DIR/undeploy_all.sh

launch microk8s kubectl create namespace $NAMESPACE

launch microk8s kubectl config set-context --current --namespace=$NAMESPACE

launch "$WORK_DIR/mqtt/deploy.sh"

launch "$PIPELINE_SERVER_WORKER_DIR/build.sh"
launch "$PIPELINE_SERVER_WORKER_DIR/deploy.sh"

launch "$WORK_DIR/haproxy/build.sh"
launch "$WORK_DIR/haproxy/deploy.sh"

if [ "$RUN_HAPROXY_BACKGROUND" == "true" ]; then
    echo "Running process to check for pipeline-server changes in the background"
    PIPELINE_SERVER_PODS=$(microk8s kubectl get pods | grep pipeline-server | awk '{ print $1 }')
    nohup $WORK_DIR/haproxy/check_for_changes.sh "$PIPELINE_SERVER_PODS" >/dev/null 2>&1 &
fi
