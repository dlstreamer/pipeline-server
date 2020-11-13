#!/bin/bash

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

REMOVE_GSTLIBAV=

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --remove-gstlibav)
        REMOVE_GSTLIBAV="--build-arg INCLUDE_GSTLIBAV=false"
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
  echo "usage: ./run_server.sh"
  echo "  [ --remove-gstlibav : Remove gstlibav package from build ] "
}

get_options "$@"



# Build VA Serving
$SAMPLE_DIR/../../docker/build.sh --framework gstreamer --create-service false --base openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10 --pipelines samples/lva_ai_extension/pipelines --models $SAMPLE_DIR/models/models.list.yml
echo $SAMPLE_DIR

VAS_BUILD_EXITCODE=$?
if [ $VAS_BUILD_EXITCODE -eq 0 ]
then
  echo "Successfully built VA parent image..."
else
  echo "Could not build VA parent image! Exit: $VAS_BUILD_EXITCODE" >&2
  exit $VAS_BUILD_EXITCODE
fi

# Build AI Extention
echo $SAMPLE_DIR/..
docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS $REMOVE_GSTLIBAV -t video-analytics-serving-lva-ai-extension $SAMPLE_DIR
