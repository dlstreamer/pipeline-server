#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#


DOCKERFILE_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname "$DOCKERFILE_DIR")

BASE_IMAGE_FFMPEG="openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg:20.10"
BASE_IMAGE_GSTREAMER="openvino/ubuntu18_runtime:2021.1"
BASE_IMAGE=
BASE_BUILD_CONTEXT=
BASE_BUILD_DOCKERFILE=
BASE_BUILD_TAG=
USER_BASE_BUILD_ARGS=
MODELS=$SOURCE_DIR/models_list/models.list.yml
MODELS_PATH=models
PIPELINES=
FRAMEWORK="gstreamer"
TAG=
RUN_PREFIX=
CREATE_SERVICE=TRUE
ENVIRONMENT_FILES=()
DOCKER_RUN_ENVIRONMENT=$(env | cut -f1 -d= | grep -E '_(proxy)$' | sed 's/^/-e / ' | tr '\n' ' ')
TARGET="deploy"

BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BASE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
BUILD_OPTIONS="--network=host "
BASE_BUILD_OPTIONS="--network=host "

SUPPORTED_IMAGES=(openvino/ubuntu18_runtime:2021.1 openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10 openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg:20.10)
OPEN_MODEL_ZOO_VERSION=
FORCE_MODEL_DOWNLOAD=

DEFAULT_GSTREAMER_BASE_BUILD_TAG="video-analytics-serving-gstreamer-base"
DEFAULT_GSTREAMER_BASE_BUILD_ARGS="--build-arg ENABLE_PAHO_INSTALLATION=true --build-arg ENABLE_RDKAFKA_INSTALLATION=true"

DEFAULT_FFMPEG_BASE_BUILD_TAG="video-analytics-serving-ffmpeg-base"
DEFAULT_FFMPEG_BASE_BUILD_ARGS=""

function launch { echo $@
    $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

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
                BASE_BUILD_CONTEXT="$2"
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
        --build-option)
            if [ "$2" ]; then
                BUILD_OPTIONS+="$2 "
                shift
            else
                error 'ERROR: "--build-option" requires an argument.'
            fi
            ;;
        --base-build-option)
            if [ "$2" ]; then
                BASE_BUILD_OPTIONS+="$2 "
                shift
            else
                error 'ERROR: "--base-build-option" requires an argument.'
            fi
            ;;
        --models)
            if [ "$2" ]; then
                MODELS=$(realpath $2)
                shift
            else
                error 'ERROR: "--models" requires an argument.'
            fi
            ;;
        --force-model-download)
            FORCE_MODEL_DOWNLOAD="--force"
            ;;
        --open-model-zoo-version)
            if [ "$2" ]; then
                OPEN_MODEL_ZOO_VERSION=$2
                shift
            else
                error 'ERROR: "--openvino-version" requires an argument.'
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
	    --environment-file)
            if [ "$2" ]; then
                ENVIRONMENT_FILES+=($2)
                shift
            else
                error 'ERROR: "--environment-file" requires an argument.'
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
	    error 'ERROR: Unknown option: ' $1
            ;;
        ?*)
	    error 'ERROR: Unknown option: ' $1
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

    if [ $FRAMEWORK != 'gstreamer' ] && [ $FRAMEWORK != 'ffmpeg' ]; then
        echo "Invalid framework"
        show_help
    fi

    if [ -z "$BASE_IMAGE" ]; then
        if [ $FRAMEWORK = 'ffmpeg' ]; then
            BASE_IMAGE=$BASE_IMAGE_FFMPEG
        else
            BASE_IMAGE=$BASE_IMAGE_GSTREAMER
        fi
    fi

    if [ -f "$MODELS" ]; then
        YML_DIR=$(dirname "${MODELS}")
        YML_FILE_NAME=$(basename "${MODELS}")
        VOLUME_MOUNT+="-v $SOURCE_DIR:/home/video-analytics-serving -v $YML_DIR:/models_yml"

        if [[ ! " ${SUPPORTED_IMAGES[@]} " =~ " ${BASE_IMAGE} " ]]; then
           if [ -z "$OPEN_MODEL_ZOO_VERSION" ]; then
            error 'ERROR: Unknown version of Intel(R) distribution of OpenVINO(TM) Toolkit in base image: '"${BASE_IMAGE}"'. Specify corresponding Open Model Zoo version for model download.'
           fi
        else
           OPEN_MODEL_ZOO_VERSION=2021.1
        fi
        
        $RUN_PREFIX docker run -t --rm $DOCKER_RUN_ENVIRONMENT --user "$UID" --entrypoint /bin/bash $VOLUME_MOUNT openvino/ubuntu18_data_dev:$OPEN_MODEL_ZOO_VERSION "-i" "-c" "pip3 install jsonschema==3.2.0; python3 /home/video-analytics-serving/tools/model_downloader --model-list /models_yml/$YML_FILE_NAME --output-dir /home/video-analytics-serving/ $FORCE_MODEL_DOWNLOAD"
   
    elif [ -d "$MODELS" ]; then
        if [ ! -d "$SOURCE_DIR/models" ]; then
            mkdir $SOURCE_DIR/models
        fi
        cp -R $MODELS/. $SOURCE_DIR/models
    else
        error 'ERROR: "'$MODELS'" does not exist.'
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

    if [ ! -z "$BASE_BUILD_CONTEXT" ]; then
        if [ -d "$BASE_BUILD_CONTEXT" ]; then
            BASE_BUILD_CONTEXT="$(realpath $BASE_BUILD_CONTEXT)"
            BASE_BUILD_DOCKERFILE="$BASE_BUILD_CONTEXT/$BASE_BUILD_DOCKERFILE"
        fi

        BASE="BUILD"
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
    echo " Building Base Image: '${BASE_BUILD_TAG}'"
    echo ""
    echo "   Build Context: '${BASE_BUILD_CONTEXT}'"
    echo "   Dockerfile: '${BASE_BUILD_DOCKERFILE}'"
    echo "   Build Options: '${BASE_BUILD_OPTIONS}'"
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
    echo "   Docker Image for downloading models: 'openvino/ubuntu18_data_dev:${OPEN_MODEL_ZOO_VERSION}'"
    echo "   Pipelines: '${PIPELINES}'"
    echo "   Framework: '${FRAMEWORK}'"
    echo "   Target: '${TARGET}'"
    echo "   Create Service: '${CREATE_SERVICE}'"
    echo "   Environment Files: '${ENVIRONMENT_FILE_LIST}'"
    echo ""
}

show_help() {
    echo "usage: build.sh"
    echo "  [--base base image]"
    echo "  [--framework ffmpeg || gstreamer]"
    echo "  [--models path to models directory or model list file or NONE]"
    echo "  [--open-model-zoo-version specify the version of openvino image to be used for downloading models from Open Model Zoo]"
    echo "  [--force-model-download force the download of models from Open Model Zoo]"
    echo "  [--pipelines path to pipelines directory relative to $SOURCE_DIR or NONE]"
    echo "  [--base-build-context docker context for building base image]"
    echo "  [--base-build-dockerfile docker file path used to build base image from build context]"
    echo "  [--build-option additional docker build option that run in the context of docker build. ex. --no-cache]"
    echo "  [--base-build-option additional docker build option for docker build of base image]"
    echo "  [--build-arg additional build args to pass to docker build]"
    echo "  [--base-build-arg additional build args to pass to docker build for base image]"
    echo "  [--tag docker image tag]"
    echo "  [--create-service create an entrypoint to run video-analytics-serving as a service]"
    echo "  [--target build a specific target]"
    echo "  [--dockerfile-dir specify a different dockerfile directory]"
    echo "  [--environment-file read and set environment variables from a file. Can be supplied multiple times.]"
    echo "  [--dry-run print docker commands without running]"
    exit 0
}

error() {
    printf '%s %s\n' "$1" "$2" >&2
    exit 1
}

if [[ "$SOURCE_DIR" =~ " " ]]; then
        error 'ERROR: Found space in path: '"$SOURCE_DIR"'. Remove space and retry.'
fi

get_options "$@"

# BUILD BASE IF BASE IS NOT SUPPLIED
if [ "$BASE" == "BUILD" ]; then
    show_base_options

    launch "$RUN_PREFIX docker build "$BASE_BUILD_CONTEXT" -f "$BASE_BUILD_DOCKERFILE" $BASE_BUILD_OPTIONS $BASE_BUILD_ARGS -t $BASE_BUILD_TAG"

    BASE_IMAGE=$BASE_BUILD_TAG
else
    #Ensure image is latest from Docker Hub
    launch "$RUN_PREFIX docker pull $BASE_IMAGE"
fi

# BUILD IMAGE

BUILD_ARGS+=" --build-arg BASE=$BASE_IMAGE "
BUILD_ARGS+=" --build-arg FRAMEWORK=$FRAMEWORK "
if [ -n "$MODELS" ]; then
    BUILD_ARGS+="--build-arg MODELS_PATH=$MODELS_PATH "
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

cp -f $DOCKERFILE_DIR/Dockerfile $DOCKERFILE_DIR/Dockerfile.env
ENVIRONMENT_FILE_LIST=

if [[ "$BASE_IMAGE" == *"openvino/"* ]]; then
    $RUN_PREFIX docker run -t --rm $DOCKER_RUN_ENVIRONMENT --entrypoint /bin/bash -e HOSTNAME=BASE $BASE_IMAGE "-i" "-c" "env" > $DOCKERFILE_DIR/openvino_base_environment.txt
    ENVIRONMENT_FILE_LIST+="$DOCKERFILE_DIR/openvino_base_environment.txt "
fi

for ENVIRONMENT_FILE in ${ENVIRONMENT_FILES[@]}; do
    if [ ! -z "$ENVIRONMENT_FILE" ]; then
	ENVIRONMENT_FILE_LIST+="$ENVIRONMENT_FILE "
    fi
done

if [ ! -z "$ENVIRONMENT_FILE_LIST" ]; then
    cat $ENVIRONMENT_FILE_LIST | grep -E '=' | tr '\n' ' ' | tr '\r' ' ' > $DOCKERFILE_DIR/final.env
    echo "ENV " | cat - $DOCKERFILE_DIR/final.env | tr -d '\n' >> $DOCKERFILE_DIR/Dockerfile.env
fi

show_image_options

launch "$RUN_PREFIX docker build -f "$DOCKERFILE_DIR/Dockerfile.env" $BUILD_OPTIONS $BUILD_ARGS -t $TAG --target $TARGET $SOURCE_DIR"
