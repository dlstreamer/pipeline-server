#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

#!/bin/bash

echo "Stopping all docker containers with name starts with video-analytics-serving"
docker stop $(docker ps -f name=video-analytics-serving) || true

echo "Removing all docker containers with name starts with video-analytics-serving"
docker rm $(docker ps -f name=video-analytics-serving) || true

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --remove)
        echo "Removing all docker images with name starts with video-analytics-serving"
        docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'video-analytics-serving') || true
        shift
        ;;
      *)
        break
        ;;
    esac

    shift
  done
}

function show_help {
  echo "usage: ./stop.sh"
  echo "  [ remove : removes all docker images starts with video-analytics-serving ]"
}

function error {
    printf '%s\n' "$1" >&2
    exit
}

get_options "$@"