#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
REMOVE_GSTLIBAV=
BASE_IMAGE="openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10"
OMZ_VERSION="2021.1"
TAG="video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension"

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --base)
        if [ "$2" ]; then
          BASE_IMAGE=$2
          shift
        else
          error 'ERROR: "--base" requires an argument.'
        fi
        ;;
      --remove-gstlibav)
        REMOVE_GSTLIBAV="--build-arg INCLUDE_GSTLIBAV=false"
        shift
        ;;
      *)
        break
        ;;
    esac

  done
}

function show_help {
  echo "usage: ./run_server.sh"
  echo "  [ --remove-gstlibav : Remove gstlibav package from build ] "
  echo "  [ --base : Base image for VA Serving build ] "
}

function launch { echo $@
    $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

get_options "$@"

# Build VA Serving
launch "$SAMPLE_DIR/../../docker/build.sh --framework gstreamer --create-service false --base $BASE_IMAGE --open-model-zoo-version $OMZ_VERSION --pipelines samples/lva_ai_extension/pipelines --models $SAMPLE_DIR/models/models.list.yml"

# Build AI Extention
echo $SAMPLE_DIR/..
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS $REMOVE_GSTLIBAV -t $TAG $SAMPLE_DIR"
