#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
MODELS="models/models.list.yml"
BASE_IMAGE=
OMZ_VERSION=
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
          BASE_IMAGE="--base $2"
          shift
        else
          error 'ERROR: "--base" requires an argument.'
        fi
        ;;
      --open-model-zoo-version)
        if [ "$2" ]; then
          OMZ_VERSION="--open-model-zoo-version $2"
          shift
        else
          error 'ERROR: "--open-model-zoo-version" requires an argument.'
        fi
        ;;
      --models)
        if [ "$2" ]; then
          MODELS=$2
          shift
        else
          error 'ERROR: "--models" requires an argument.'
        fi
        ;;
      *)
        break
        ;;
    esac

  done
}

function show_help {
  echo "usage: ./run_server.sh"
  echo "  [ --base : Base image for VA Serving build ] "
  echo "  [ --open-model-zoo-version : Open Model Zoo version override for VA Serving build ] "
  echo "  [ --models : Model list, must be a relative path ] "
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
launch "$SAMPLE_DIR/../../docker/build.sh --framework gstreamer --create-service false $BASE_IMAGE $OMZ_VERSION --pipelines samples/lva_ai_extension/pipelines --models $SAMPLE_DIR/$MODELS"

# Build AI Extention
echo $SAMPLE_DIR/..
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t $TAG $SAMPLE_DIR"
