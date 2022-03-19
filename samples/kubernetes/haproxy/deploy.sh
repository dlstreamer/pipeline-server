#!/bin/bash -e


WORK_DIR=$(dirname $(readlink -f "$0"))
HAPROXY_YAML=${WORK_DIR}/haproxy.yaml

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

launch microk8s kubectl apply -f $HAPROXY_YAML

sleep 5

microk8s kubectl rollout restart deploy haproxy-deployment

sleep 10

for (( i=0; i<10; ++i)); do
    terminating=$(microk8s kubectl get pods | grep "haproxy" | awk '{ print $3 }' | grep  'Terminating' | wc -l)
    echo "Waiting for haproxy service to start......."
    if [ $terminating == 0 ]; then
        echo "HAProxy Service started"
        break
    else
        sleep 10
    fi
done

echo "$(microk8s kubectl get pods)"