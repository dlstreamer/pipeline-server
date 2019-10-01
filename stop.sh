#!/bin/bash -e
stop_gstreamer () {
  docker stop video_analytics_serving_gstreamer
}
stop_ffmpeg () {
  docker stop video_analytics_serving_ffmpeg
}

if [ $# -eq 0 ]; then
  stop_gstreamer
else
  build="$1"
  if [ "$build" = "ffmpeg" ]; then
    stop_ffmpeg
  else
    stop_gstreamer
  fi
fi
