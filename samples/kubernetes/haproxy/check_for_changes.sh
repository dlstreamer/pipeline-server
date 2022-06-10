#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

PIPELINE_SERVER_PODS=${PIPELINE_SERVER_PODS:-$1}
echo $PIPELINE_SERVER_PODS
echo "Starting loop to look for any changes in Pipeline Servers"

while true
do
  sleep 10
  echo "looking for changes in Pipeline Servers"
  pods=$(microk8s kubectl get pods | grep "pipeline-server.*worker" | grep 'Running' | awk '{ print $1 " " $4}')
  if [ "$PIPELINE_SERVER_PODS" != "$pods" ]; then
    echo "Pipeline server pod added or restarted"
    echo "$pods"
    launch $WORK_DIR/build.sh
    launch $WORK_DIR/deploy.sh
    PIPELINE_SERVER_PODS=$(microk8s kubectl get pods | grep "pipeline-server.*worker" | grep 'Running' | awk '{ print $1 " " $4}')
  fi
done
echo "exited"
