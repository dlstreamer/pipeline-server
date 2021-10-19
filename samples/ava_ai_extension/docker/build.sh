#!/bin/bash -e

CURRENT_DIR=$(dirname $(readlink -f "$0"))
ROOT_DIR=$(dirname $CURRENT_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
MODELS="$ROOT_DIR/models_list/models.list.yml"
TAG="video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension"
FORCE_MODEL_DOWNLOAD=
VAS_BASE="video-analytics-serving-runtime:latest"
VAS_VER="v0.6.1-beta"
VAS_REPO="https://github.com/intel/video-analytics-serving"
BASE_IMAGE=
VAS_DIR=

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
      --base)
        if [ "$2" ]; then
            BASE_IMAGE=$2
            shift
        else
            error 'ERROR: "--base" requires an argument.'
        fi
        ;;
      --vas-dir)
        if [ "$2" ]; then
            VAS_DIR=$(realpath $2)
            shift
        else
            error 'ERROR: "--vas-dir" requires an argument.'
        fi
        ;;
      --tag)
        if [ "$2" ]; then
            TAG=$2
            shift
        else
            error 'ERROR: "--tag" requires an argument.'
        fi
        ;;
      --force-model-download)
        FORCE_MODEL_DOWNLOAD="--force"
        ;;
      *)
        break
        ;;
    esac
    shift
  done
}

function show_help {
  echo "usage: ./build.sh"
  echo "  [ --models : Model list, must be a relative path ] "
  echo " [--force-model-download : force the download of models even if models exists] "
  echo " [--base : base image] "
  echo " [--vas-dir : path to local video-analytics-serving directory] "
  echo " [--tag docker image tag] "
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

if [ ! -z "$VAS_DIR" ]; then
    echo "Using video-analytics-serving from $VAS_DIR"
else
    VAS_DIR="$CURRENT_DIR/.video-analytics-serving"
    rm -rf $VAS_DIR
    mkdir -p $VAS_DIR
    echo "Downloading video-analytics-serving from $VAS_REPO version $VAS_VER"
    wget $VAS_REPO/tarball/$VAS_VER -P $VAS_DIR
    tar -xvf "$VAS_DIR/$VAS_VER" -C $VAS_DIR --strip-components 1 >&/dev/null
fi

echo "Downloading models"
$VAS_DIR/tools/model_downloader/model_downloader.sh --model-list "$MODELS" \
      --output "$ROOT_DIR" $FORCE_MODEL_DOWNLOAD

if [ -z "$BASE_IMAGE" ]; then
    echo "Building video-analytics-serving as $VAS_BASE"
    launch "$VAS_DIR/docker/build.sh --framework gstreamer --create-service false \
            --models NONE --tag $VAS_BASE"
            #TODO: Set --pipelines NONE for 0.7 release, currently external github doesn't copy extensions with --pipelines NONE
            #--pipelines NONE --models NONE --tag $VAS_BASE"
else
    echo "Using Base image $BASE_IMAGE"
    BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
fi

rm -rf "$CURRENT_DIR/.video-analytics-serving"

# Build AI Extention
launch "docker build -f $CURRENT_DIR/Dockerfile $BUILD_ARGS -t $TAG $ROOT_DIR"
