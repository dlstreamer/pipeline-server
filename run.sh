#!/bin/bash -e
run_gstreamer () {
sudo docker run -e http_proxy=$http_proxy -e https_proxy=$https_proxy -p 8080:8080 -v /tmp:/tmp --rm video_analytics_serving_gstreamer:latest
}
run_ffmpeg () {
sudo docker run -e http_proxy=$http_proxy -e https_proxy=$https_proxy -p 8080:8080 -v /tmp:/tmp --rm video_analytics_serving_ffmpeg:latest
}
if [ $# -eq 0 ]
  then
  run_gstreamer
else
  build="$1"
  if [ "$build" = "ffmpeg" ]; then
     run_ffmpeg
  else
     run_gstreamer
  fi
fi
