#!/bin/bash
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

echo "Stopping pipeline server containers"
docker stop $(docker ps -q -f name=dlstreamer-pipeline-server) 2> /dev/null || echo "No containers to stop"

echo "Removing pipeline server containers"
docker rm $(docker ps -q -f name=dlstreamer-pipeline-server) 2> /dev/null || echo "No containers to remove"

function show_help {
  echo "usage: ./stop.sh"
  echo "  [ --remove : remove pipeline server images ]"
  echo "  [ --clean-shared-memory : remove files in /dev/shm to clean up shared memory ]"
}

while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    --remove)
      echo "Removing pipeline server images"
      docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'dlstreamer-pipeline-server') 2> /dev/null || echo "No images to remove"
      ;;
    --clean-shared-memory)
      echo "Removing all files in /dev/shm"
      rm /dev/shm/* 2> /dev/null || echo "No files to remove in /dev/shm"
      ;;
    --all)
      echo "Stopping ALL containers"
      docker stop $(docker ps -q) 2> /dev/null || echo "No containers to stop"
      echo "killing ALL containers not responsive to stop"
      docker kill $(docker ps -q) 2> /dev/null || echo "No containers to kill"
      echo "Removing ALL containers"
      docker rm $(docker ps -a -q) 2> /dev/null || echo "No containers to remove"
      ;;
    *)
      break
      ;;
  esac

  shift
done
echo "Exiting"
exit 0