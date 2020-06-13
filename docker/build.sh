#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

BASE_IMAGE=
BASE_BUILD_CONTEXT=
BASE_BUILD_DOCKERFILE=
BASE_BUILD_TAG=
USER_BASE_BUILD_ARGS=
MODELS=models
PIPELINES=
FRAMEWORK=
TAG=
RUN_PREFIX=
CREATE_SERVICE=TRUE
TARGET="deploy"

DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $DOCKERFILE_DIR)
BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BASE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host"

DEFAULT_GSTREAMER_BASE_BUILD_CONTEXT="https://github.com/opencv/gst-video-analytics.git#v1.0.0"
DEFAULT_GSTREAMER_BASE_BUILD_DOCKERFILE="docker/Dockerfile"
DEFAULT_GSTREAMER_BASE_BUILD_TAG="video-analytics-serving-gstreamer-base"
DEFAULT_GSTREAMER_BASE_BUILD_ARGS="--build-arg ENABLE_PAHO_INSTALLATION=true --build-arg ENABLE_RDKAFKA_INSTALLATION=true"

DEFAULT_FFMPEG_BASE_BUILD_CONTEXT="https://github.com/nnshah1/FFmpeg-patch.git#669e8e6d3f88416ab367e442f0b42b1314b8ffe2:docker"
DEFAULT_FFMPEG_BASE_BUILD_DOCKERFILE="Dockerfile.source"
DEFAULT_FFMPEG_BASE_BUILD_TAG="video-analytics-serving-ffmpeg-base"
DEFAULT_FFMPEG_BASE_BUILD_ARGS=""

get_options() {
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
        --target)
            if [ "$2" ]; then
                TARGET=$2
                shift
            else
                error 'ERROR: "--target" requires an argument.'
            fi
            ;;
        --base-build-context)
            if [ "$2" ]; then
                BASE_BUILD_CONTEXT=$2
                shift
            else
                error 'ERROR: "--base-build-context" requires an argument.'
            fi
            ;;
        --base-build-dockerfile)
            if [ "$2" ]; then
                BASE_BUILD_DOCKERFILE=$2
                shift
            else
                error 'ERROR: "--base-build-dockerfile" requires an argument.'
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
        --pipelines)
            if [ "$2" ]; then
                PIPELINES=$2
                shift
            else
                error 'ERROR: "--pipelines" requires an argument.'
            fi
            ;;
        --framework)
            if [ "$2" ]; then
                FRAMEWORK=$2
                shift
            else
                error 'ERROR: "--framework" requires an argument.'
            fi
            ;;
        --build-arg)
            if [ "$2" ]; then
                BUILD_ARGS+="--build-arg $2 "
                shift
            else
                error 'ERROR: "--build-arg" requires an argument.'
            fi
            ;;
        --base-build-arg)
            if [ "$2" ]; then
                USER_BASE_BUILD_ARGS+="--build-arg $2 "
                shift
            else
                error 'ERROR: "--base-build-arg" requires an argument.'
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
        --dockerfile-dir)
            if [ "$2" ]; then
                DOCKERFILE_DIR=$2
                shift
            else
                error 'ERROR: "--dockerfile-dir" requires an argument.'
            fi
            ;;
        --create-service)
            if [ "$2" ]; then
                CREATE_SERVICE=${2^^}
                shift
            else
                error 'ERROR: "--create-service" requires an argument.'
            fi
            ;;
        --dry-run)
            RUN_PREFIX="echo"
            echo ""
            echo "=============================="
            echo "DRY RUN: COMMANDS PRINTED ONLY"
            echo "=============================="
            echo ""
            ;;
        --)
            shift
            break
            ;;
        -?*)
            printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
            ;;
        *)
            break
            ;;
        esac

        shift
    done

    if [ "${MODELS^^}" == "NONE" ]; then
        MODELS=
    fi

    if [ -z "$FRAMEWORK" ]; then
        FRAMEWORK="gstreamer"
    elif [ $FRAMEWORK != 'gstreamer' ] && [ $FRAMEWORK != 'ffmpeg' ]; then
        echo "Invalid framework"
        show_help
    fi

    if [ -z "$PIPELINES" ]; then
        PIPELINES=pipelines/$FRAMEWORK
    elif [ "${PIPELINES^^}" == "NONE" ]; then
        PIPELINES=
    fi

    if [[ -n "$BASE_BUILD_CONTEXT" && -z "$BASE_BUILD_DOCKERFILE" ]]; then
        error 'ERROR: setting "--base-build-context" requires setting "--base-build-dockerfile"'
    elif [[ -z "$BASE_BUILD_CONTEXT" && -n "$BASE_BUILD_DOCKERFILE" ]]; then
        error 'ERROR: setting "--base-build-dockerfile" requires setting "--base-build-context"'
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
        if [ -z "$USER_BASE_BUILD_ARGS" ]; then
            USER_BASE_BUILD_ARGS=DEFAULT_${FRAMEWORK^^}_BASE_BUILD_ARGS
            USER_BASE_BUILD_ARGS=${!USER_BASE_BUILD_ARGS}
        fi
        BASE_BUILD_ARGS+=$USER_BASE_BUILD_ARGS
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
    echo "   Build Arguments: '${BASE_BUILD_ARGS}'"
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
    echo "   Target: '${TARGET}'"
    echo "   Create Service: '${CREATE_SERVICE}'"
    echo ""
}

show_help() {
    echo "usage: build.sh"
    echo "  [--base base image]"
    echo "  [--framework ffmpeg || gstreamer]"
    echo "  [--models path to model directory relative to $SOURCE_DIR or NONE]"
    echo "  [--pipelines path to pipelines directory relative to $SOURCE_DIR or NONE]"
    echo "  [--build-arg additional build args to pass to docker build]"
    echo "  [--base-build-arg additional build args to pass to docker build for base image]"
    echo "  [--create-service create an entrypoint to run video-analytics-serving as a service]"
    echo "  [--target build a specific target]"
    echo "  [--dockerfile-dir specify a different dockerfile directory]"
    echo "  [--dry-run print docker commands without running]"
    exit 0
}

error() {
    printf '%s\n' "$1" >&2
    exit 1
}

get_options "$@"

# BUILD BASE IF BASE IS NOT SUPPLIED

if [ "$BASE" == "BUILD" ]; then
    show_base_options

    if [ -z "$RUN_PREFIX" ]; then
        set -x
    fi

    $RUN_PREFIX docker build "$BASE_BUILD_CONTEXT" -f "$BASE_BUILD_DOCKERFILE" $BUILD_OPTIONS $BASE_BUILD_ARGS -t $BASE_BUILD_TAG

    { set +x; } 2>/dev/null
    BASE_IMAGE=$BASE_BUILD_TAG
fi

# BUILD IMAGE

BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
BUILD_ARGS+=" --build-arg FRAMEWORK=$FRAMEWORK "
if [ -n "$MODELS" ]; then
    BUILD_ARGS+="--build-arg MODELS_PATH=$MODELS "
    BUILD_ARGS+="--build-arg MODELS_COMMAND=copy_models "
else
    BUILD_ARGS+="--build-arg MODELS_COMMAND=do_not_copy_models "
fi

if [ -n "$PIPELINES" ]; then
    BUILD_ARGS+="--build-arg PIPELINES_PATH=$PIPELINES "
    BUILD_ARGS+="--build-arg PIPELINES_COMMAND=copy_pipelines "
else
    BUILD_ARGS+="--build-arg PIPELINES_COMMAND=do_not_copy_pipelines "
fi

if [ "$CREATE_SERVICE" == "TRUE" ]; then
    BUILD_ARGS+="--build-arg FINAL_STAGE=video-analytics-serving-service "
else
    BUILD_ARGS+="--build-arg FINAL_STAGE=video-analytics-serving-library "
fi

show_image_options

if [ -z "$RUN_PREFIX" ]; then
    set -x
fi
$RUN_PREFIX docker build -f "$DOCKERFILE_DIR/Dockerfile" $BUILD_OPTIONS $BUILD_ARGS -t $TAG --target $TARGET $SOURCE_DIR

{ set +x; } 2>/dev/null
