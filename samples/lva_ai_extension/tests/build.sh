#!/bin/bash -e
WORK_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(readlink -f "$WORK_DIR/../../..")
LVA_DIR=$(dirname $WORK_DIR)
EXTENSION_IMAGE_TAG="video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension"
TEST_IMAGE_TAG="video-analytics-serving-lva-tests"
SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --lva-image)
        if [ "$2" ]; then
          LVA_IMAGE=$2
          SAMPLE_BUILD_ARGS+=" --build-arg BASE=$LVA_IMAGE"
          shift
        else
          error 'ERROR: "--lva-image" requires an argument.'
        fi
        ;;
      --docker-cache)
        if [ "$2" ]; then
          CACHE_PREFIX=$2
          shift
        else
          error 'ERROR: "--docker-cache" requires an argument.'
        fi
        ;;
      # For backwards compatbility with scripts that took cache prefix as $1
      *cache*)
        CACHE_PREFIX=$1
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
  echo "  [ --lva-image : LVA extension image to base test image on ] "
  echo "  [ --docker-cache : Docker cache prefix ] "
}

get_options "$@"

# Build LVA image if not specified
if [ -z "$LVA_IMAGE" ]; then
    echo Building $EXTENSION_IMAGE_TAG
    # Export to allow nested scripts to digest CACHE_PREFIX
    export CACHE_PREFIX=${CACHE_PREFIX}
    launch "$LVA_DIR/docker/build.sh"
fi

# Add tests layer
echo "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t $TEST_IMAGE_TAG $WORK_DIR"
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS -t $TEST_IMAGE_TAG $WORK_DIR"
