
#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

SCRIPT_DIR=$(dirname $(readlink -f "$0"))
WORK_DIR="$SCRIPT_DIR/docker"
CONFIG_DIR=$WORK_DIR/generated
HAPROXY_CONFIG_FILE=$CONFIG_DIR/haproxy.cfg
HAPROXY_CONFIG_TEMPLATE=$WORK_DIR/haproxy-template.cfg
HAPROXY_MAP_FILE=$CONFIG_DIR/servers.map
POST_SERVER_DETAILS=
POST_SERVER_STRING="    server server-name server-address:8080 check weight 100 agent-check agent-addr server-address agent-port 3333 agent-inter 1s  agent-send ping"
NEWLINE=$'\n'
PIPELINE_SERVER="pipeline-server"
GET_SERVER_STRING="  server server-name server-address:8080 check"


running=0
for (( i=0; i<20; ++i)); do
    running=$(microk8s kubectl get pods | grep "pipeline-server" | awk '{ print $3 }' | grep  'Running' | wc -l)
    if [ $running -gt 0 ]; then
        echo " $running pipeline-server services running "
        break
    else
        echo "No pipeline-server services are running"
        echo "$(microk8s kubectl get pods | grep "pipeline-server")"
        sleep 10
    fi
done

if [ $running == 0 ]; then
    echo "Failed to run pipeline server services, wait for some time and check if pipeline server pods are running and rerun the script"
    exit 1
fi


echo "Building HA PRoxy image with config files"

rm -rf $CONFIG_DIR
mkdir $CONFIG_DIR

cp $HAPROXY_CONFIG_TEMPLATE $HAPROXY_CONFIG_FILE
touch $HAPROXY_MAP_FILE

IPS=$(microk8s kubectl describe service pipeline-server | grep Endpoints: | sed 's/Endpoints://g'| sed 's/ //g' | head -n 1)
IFS=', ' read -r -a array <<< "$IPS"
for index in "${!array[@]}"
do
   value=${array[index]}
   server=${value%:*}
   server_name=${server//./}_server
   post_server_line=${POST_SERVER_STRING//server-address/$server}
   post_server_line=${post_server_line/server-name/$server_name}
   POST_SERVER_DETAILS="${POST_SERVER_DETAILS}${post_server_line}${NEWLINE}"

   get_server_line=${GET_SERVER_STRING//server-address/$server}
   get_server_line=${get_server_line/server-name/$server_name}
   backend_name=${PIPELINE_SERVER}${index}
   echo $NEWLINE >> $HAPROXY_CONFIG_FILE
   echo "backend ${backend_name}" >> $HAPROXY_CONFIG_FILE
   echo "$get_server_line" >> $HAPROXY_CONFIG_FILE

   telnet_output=$(sleep 1 | telnet $server 4444 | sed -ne '/Escape character is/,$ p' | tail -1)
   echo "$telnet_output $backend_name" >> $HAPROXY_MAP_FILE
done

FILE_OUTPUT="$(awk -v r="$POST_SERVER_DETAILS" '{gsub(/this line is updated by script/,r)}1' $HAPROXY_CONFIG_FILE )"

echo "$FILE_OUTPUT" > $HAPROXY_CONFIG_FILE

HAPROXY_WITH_CONFIG_IMAGE=${HAPROXY_WITH_CONFIG_IMAGE:-"localhost:32000/haproxy-with-config:latest"}

echo "Building HA Proxy image with config files"

docker build -t $HAPROXY_WITH_CONFIG_IMAGE $WORK_DIR

echo "Pushing $HAPROXY_WITH_CONFIG_IMAGE into k8s registry..."
docker push $HAPROXY_WITH_CONFIG_IMAGE