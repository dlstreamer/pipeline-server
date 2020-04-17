#!/bin/bash -e
#
# Copyright (C) 2019 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

BASE_IMAGE=
BASE_BUILD_CONTEXT=
BASE_BUILD_DOCKERFILE=
BASE_BUILD_TAG=
MODELS=
PIPELINES=
FRAMEWORK=
TAG=
RUN_PREFIX=
CREATE_ENTRYPOINT=

DEFAULT_GSTREAMER_BASE_BUILD_CONTEXT="https://github.com/opencv/gst-video-analytics.git#v1.0.0"
DEFAULT_GSTREAMER_BASE_BUILD_DOCKERFILE="docker/Dockerfile"
DEFAULT_GSTREAMER_BASE_BUILD_TAG="video-analytics-serving-gstreamer-base"

DEFAULT_FFMPEG_BASE_BUILD_CONTEXT="https://github.com/VCDP/FFmpeg-patch.git#a96d280226e964639f076f8e9c55c0a71cb2e3ad:docker"
DEFAULT_FFMPEG_BASE_BUILD_DOCKERFILE="Dockerfile.source"
DEFAULT_FFMPEG_BASE_BUILD_TAG="video-analytics-serving-ffmpeg-base"


DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host"

get_options() {
while :; do
    case $1 in
        -h|-\?|--help)
            show_help    # Display a usage synopsis.
            exit
            ;;
        --base)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                BASE_IMAGE=$2
                shift
            else
                error 'ERROR: "--base" requires a non-empty option argument.'
            fi
            ;;
        --base-build-context)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                BASE_BUILD_CONTEXT=$2
                shift
            else
                error 'ERROR: "--base-build-context" requires a non-empty option argument.'
            fi
            ;;
        --base-build-dockerfile)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                BASE_BUILD_DOCKERFILE=$2
                shift
            else
                error 'ERROR: "--base-build-dockerfile" requires a non-empty option argument.'
            fi
            ;;
        --models)
           if [ "$2" ]; then
                MODELS=$2
                shift
            else
                error 'ERROR: "--models" requires a non-empty option argument.'
            fi
            ;;
        --pipelines)
           if [ "$2" ]; then
                PIPELINES=$2
                shift
            else
                error 'ERROR: "--pipelines" requires a non-empty option argument.'
            fi
            ;;
        --framework)
           if [ "$2" ]; then
                FRAMEWORK=$2
                shift
            else
                error 'ERROR: "--framework" requires a non-empty option argument.'
            fi
            ;;
        --build-arg)
           if [ "$2" ]; then
                BUILD_ARGS+="--build-arg $2 "
                shift
            else
                error 'ERROR: "--build-arg" requires a non-empty option argument.'
            fi
            ;;
        --tag)
           if [ "$2" ]; then
                TAG=$2
                shift
            else
                error 'ERROR: "--tag" requires a non-empty option argument.'
            fi
            ;;
        --create-entrypoint)
            CREATE_ENTRYPOINT=TRUE
            ;;
        --dry-run)
            RUN_PREFIX="echo"
            echo ""
            echo "=============================="
            echo "DRY RUN: COMMANDS PRINTED ONLY"
            echo "=============================="
            echo ""
            ;;
         --)              # End of all options.
            shift
            break
            ;;
        -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
            ;;
        *)               # Default case: No more options, so break out of the loop.
            break
    esac

    shift
done

if [ -z "$FRAMEWORK" ]; then
  FRAMEWORK="gstreamer"
elif [ $FRAMEWORK != 'gstreamer' ] && [ $FRAMEWORK != 'ffmpeg' ]; then
  echo "Invalid framework"
  show_help
fi

if [ -z "$BASE_IMAGE" ]; then
  BASE="BUILD"
  if [ -z "$BASE_BUILD_CONTEXT" ]; then
   BASE_BUILD_CONTEXT=DEFAULT_${FRAMEWORK^^}_BASE_BUILD_CONTEXT
   BASE_BUILD_CONTEXT=${!BASE_BUILD_CONTEXT}  
  fi
  if [ -z "$BASE_BUILD_DOCKERFILE" ]; then
   BASE_BUILD_DOCKERFILE=DEFAULT_${FRAMEWORK^^}_BASE_BUILD_DOCKERFILE
   BASE_BUILD_DOCKERFILE=${!BASE_BUILD_DOCKERFILE}  
  fi
  if [ -z "$BASE_BUILD_TAG" ]; then
   BASE_BUILD_TAG=DEFAULT_${FRAMEWORK^^}_BASE_BUILD_TAG  
   BASE_BUILD_TAG=${!BASE_BUILD_TAG}
  fi
else
  BASE="IMAGE"
fi

if [ -z "$TAG" ]; then
  TAG="video-analytics-serving-${FRAMEWORK}"
fi
}

show_base_options() {
       echo ""
       echo "Building Base Image: '${BASE_BUILD_TAG}'"
       echo ""
       echo "   Build Context: '${BASE_BUILD_CONTEXT}'"
       echo "   Dockerfile: '${BASE_BUILD_DOCKERFILE}'"
       echo "   Build Options: '${BUILD_OPTIONS}'"
       echo "   Build Arguments: '${BUILD_ARGS}'" 
       echo ""
}

show_image_options() {
       echo ""
       echo "Building Video Analytics Serving Image: '${TAG}'"
       echo ""
       echo "   Base: '${BASE_IMAGE}'"
       echo "   Build Context: '${SOURCE_DIR}'"
       echo "   Dockerfile: '${DOCKERFILE_DIR}/Dockerfile'"
       echo "   Build Options: '${BUILD_OPTIONS}'"
       echo "   Build Arguments: '${BUILD_ARGS}'" 
       echo "   Models: '${MODELS}'" 
       echo "   Pipelines: '${PIPELINES}'" 
       echo "   Framework: '${FRAMEWORK}'" 
       echo ""
}

show_help() {
  echo "usage: build.sh" 
  echo "  [--base base image]"
  echo "  [--framework ffmpeg || gstreamer]"
  echo "  [--models path to model directory]" 
  echo "  [--pipelines path to pipelines directory]"
  echo "  [--build-arg additional build args to pass to docker build]"
  echo "  [--create-entrypoint create an entrypoint to run video-analytics-serving as a service]"
  echo "  [--dry-run print docker commands without running]"
  exit 0
}

error() {
    printf '%s\n' "$1" >&2
    exit d
}

get_options "$@"



# BUILD BASE IF BASE IS NOT SUPPLIED

if [ $BASE == "BUILD" ]; then
 show_base_options

 if [ -z "$RUN_PREFIX" ]; then
  set -x
 fi

 $RUN_PREFIX docker build $BASE_BUILD_CONTEXT -f $BASE_BUILD_DOCKERFILE $BUILD_OPTIONS $BUILD_ARGS -t $BASE_BUILD_TAG

 { set +x; } 2>/dev/null
 BASE_IMAGE=$BASE_BUILD_TAG
fi

# BUILD IMAGE

BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
BUILD_ARGS+=" --build-arg FRAMEWORK=$FRAMEWORK "
if [ ! -z "$MODELS" ]; then
    BUILD_ARGS+="--build-arg MODELS_PATH=$MODELS "
    BUILD_ARGS+="--build-arg MODELS_COMMAND=copy_models "
else
    BUILD_ARGS+="--build-arg MODELS_COMMAND=do_not_copy_models "
fi

if [ ! -z "$PIPELINES" ]; then
    BUILD_ARGS+="--build-arg PIPELINES_PATH=$PIPELINES "
    BUILD_ARGS+="--build-arg PIPELINES_COMMAND=copy_pipelines "
else
    BUILD_ARGS+="--build-arg PIPELINES_COMMAND=do_not_copy_pipelines "
fi

if [ $CREATE_ENTRYPOINT == TRUE ]; then
   BUILD_ARGS+="--build-arg FINAL_STAGE=video-analytics-serving-service "
else
   BUILD_ARGS+="--build-arg FINAL_STAGE=video-analytics-serving-environment "
fi

show_image_options

if [ -z "$RUN_PREFIX" ]; then
  set -x
 fi
$RUN_PREFIX docker build -f $DOCKERFILE_DIR/Dockerfile $BUILD_OPTIONS $BUILD_ARGS -t $TAG $SOURCE_DIR

{ set +x; } 2>/dev/null
