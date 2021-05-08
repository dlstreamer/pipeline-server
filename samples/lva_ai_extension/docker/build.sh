#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
MODELS="models/models.list.yml"
TAG="video-analytics-serving:0.5.1-dlstreamer-edge-ai-extension"

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
      *)
        break
        ;;
    esac

  done
}

function show_help {
  echo "usage: ./build.sh"
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
launch "$SAMPLE_DIR/../../docker/build.sh --framework gstreamer --create-service false --pipelines samples/lva_ai_extension/pipelines --models $SAMPLE_DIR/$MODELS"

# Build AI Extention
echo $SAMPLE_DIR/..
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t $TAG $SAMPLE_DIR"
