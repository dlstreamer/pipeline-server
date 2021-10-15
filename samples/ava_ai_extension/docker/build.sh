#!/bin/bash -e

CURRENT_DIR=$(dirname $(readlink -f "$0"))
VAS_DIR=$(readlink -f "$CURRENT_DIR/../../..")
AVA_DIR=$(dirname $CURRENT_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
MODELS="$AVA_DIR/models_list/models.list.yml"
TAG="video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension"
FORCE_MODEL_DOWNLOAD=
VAS_BASE="video-analytics-serving-runtime:latest"

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --models)
        if [ "$2" ]; then
          MODELS=$2
          shift
        else
          error 'ERROR: "--models" requires an argument.'
        fi
        ;;
      --force-model-download)
        FORCE_MODEL_DOWNLOAD="--force"
        ;;
      *)
        break
        ;;
    esac

  done
}

function show_help {
  echo "usage: ./build.sh"
  echo "  [ --models : Model list, must be a relative path ] "
  echo " [--force-model-download : force the download of models even if models exists] "
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
launch "$VAS_DIR/docker/build.sh --framework gstreamer --create-service false \
          --pipelines NONE --models NONE --tag $VAS_BASE"

# Downloading models
$VAS_DIR/tools/model_downloader/model_downloader.sh --model-list "$MODELS" \
          --output "$AVA_DIR" $FORCE_MODEL_DOWNLOAD

# Build AI Extention
echo $AVA_DIR/..
launch "docker build -f $CURRENT_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t $TAG $AVA_DIR"
