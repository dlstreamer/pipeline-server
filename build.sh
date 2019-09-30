#!/bin/bash -e
echo "IMPORTANT: Video Analytics Serving is a sample. The project provides a reference architecture with straightforward examples to accelerate your implementation of a solution. However, it is not intended for production. In addition to modifying pipelines and models to fit your use cases, you must harden security of endpoints and other critical tasks to secure your solution."
build_gstreamer () {
  sudo docker build -f Dockerfile.gst.base -t video_analytics_serving_gstreamer_base $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /') .
  sudo docker build -f Dockerfile.gst -t video_analytics_serving_gstreamer $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /') .
}
build_ffmpeg () {
  sudo docker build -f Dockerfile.ffmpeg.base -t video_analytics_serving_ffmpeg_base $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /') .
  sudo docker build -f Dockerfile.ffmpeg -t video_analytics_serving_ffmpeg $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /') .
}
if [ $# -eq 0 ]; then
  build_gstreamer
  build_ffmpeg
else
  build="$1"
  if [ "$build" = "ffmpeg" ]; then
    build_ffmpeg
  else
    build_gstreamer
  fi
fi
