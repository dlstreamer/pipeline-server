#!/bin/bash
END=10

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/../../../docker"

for i in $(seq 1 $END);
do
    ./run_client.sh &
done
