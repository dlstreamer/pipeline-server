#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
ADD_PROXY_ENV=${ADD_PROXY_ENV:-true}
PIPELINE_SERVER_YAML=${WORK_DIR}/pipeline-server.yaml

if [ "$ADD_PROXY_ENV" == "true" ]; then
    echo "Adding proxy settings to $PIPELINE_SERVER_YAML"
    PROXY_CONFIG=
    NEWLINE=$'\n'

    if [[ ! -z "$http_proxy" && -z $(grep -R http_proxy $PIPELINE_SERVER_YAML) ]]; then
        PROXY_CONFIG=${PROXY_CONFIG}"            - name: http_proxy"${NEWLINE}
        PROXY_CONFIG=${PROXY_CONFIG}"              value: "${http_proxy}${NEWLINE}
    fi

    if [[ ! -z "$https_proxy" && -z $(grep -R https_proxy $PIPELINE_SERVER_YAML) ]]; then
        PROXY_CONFIG=${PROXY_CONFIG}"            - name: https_proxy"${NEWLINE}
        PROXY_CONFIG=${PROXY_CONFIG}"              value: "${https_proxy}${NEWLINE}
    fi

    if [[ ! -z "$no_proxy" && -z $(grep -R no_proxy $PIPELINE_SERVER_YAML) ]]; then
        PROXY_CONFIG=${PROXY_CONFIG}"            - name: no_proxy"${NEWLINE}
        PROXY_CONFIG=${PROXY_CONFIG}"              value: "${no_proxy}${NEWLINE}
    fi

    if [ ! -z "$PROXY_CONFIG" ]; then
        PROXY_CONFIG="          env:${NEWLINE}${PROXY_CONFIG}"
        FILE_OUTPUT="$(awk -v r="$PROXY_CONFIG" '{gsub(/          env:/,r)}1' $PIPELINE_SERVER_YAML )"
        echo "$FILE_OUTPUT" > $PIPELINE_SERVER_YAML
    fi

fi

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

echo "Using $PIPELINE_SERVER_YAML to deploy pipeline server"
launch microk8s kubectl apply -f $PIPELINE_SERVER_YAML

sleep 10

not_running=0
for (( i=0; i<25; ++i)); do
    not_running=$(microk8s kubectl get pods | grep "pipeline-server" | grep -vE 'Running' | wc -l)
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
