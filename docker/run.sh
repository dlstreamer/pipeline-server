#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# modes 
# Dev: priviledged, volume mount source, bash entrypoint, volume mount models and pipelines (default or specified)
# Service: expose port, volume mount models and pipelines if specified, entrypoint python3 -m openapiserver
# mount anything else that is passed as -v, graphics device
# name is video-analytics-serving-gstreamer
# name is video-analytics-serving-ffmpeg
# dev network = host

MODELS=
PIPELINES=
FRAMEWORK=
IMAGE=
VOLUME_MOUNT=
MODE=SERVICE
PORTS=
DEVICES=
DEFAULT_GSTREAMER_IMAGE="video-analytics-serving-gstreamer"
DEFAULT_FFMPEG_IMAGE="video-analytics-serving-ffmpeg"
ENTRYPOINT=
PRIVILEGED=
NETWORK=
USER=

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)
ENVIRONMENT=$(env | cut -f1 -d= | grep -E '_(proxy)$' | sed 's/^/-e / ' | tr '\n' ' ')


get_options() {
while :; do
    case $1 in
        -h|-\?|--help)
            show_help    # Display a usage synopsis.
            exit
            ;;
        --image)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                IMAGE=$2
                shift
            else
                error 'ERROR: "--image" requires a non-empty option argument.'
            fi
            ;;
        --models)
           if [ "$2" ]; then
                MODELS=$(realpath $2)
                shift
            else
                error 'ERROR: "--models" requires a non-empty option argument.'
            fi
           ;;
	--user)
           if [ "$2" ]; then
                USER="--user $2"
                shift
            else
                error 'ERROR: "--models" requires a non-empty option argument.'
            fi
            ;;
        --pipelines)
           if [ "$2" ]; then
                PIPELINES=$(realpath $2)
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
        -e)
           if [ "$2" ]; then
                ENVIRONMENT+="-e $2 "
                shift
            else
                error 'ERROR: "-e" requires a non-empty option argument.'
            fi
            ;;
        -p)
           if [ "$2" ]; then
                PORTS+="-p $2 "
                shift
            else
                error 'ERROR: "-p" requires a non-empty option argument.'
            fi
            ;;
        -v)
           if [ "$2" ]; then
                VOLUME_MOUNT+="-v $2 "
                shift
            else
                error 'ERROR: "-v" requires a non-empty option argument.'
            fi
            ;;
        --dev)
            MODE=DEV
            ;;
        --name)
            if [ "$2" ]; then
                NAME=$2
                shift
            else
                error 'ERROR: "--name" requires a non-empty option argument.'
            fi
            ;;
        --network)
            if [ "$2" ]; then
                NETWORK="--network $2"
                shift
            else
                error 'ERROR: "--network" requires a non-empty option argument.'
            fi
            ;;
        --entrypoint)
            if [ "$2" ]; then
                ENTRYPOINT="--entrypoint $2"
                shift
            else
                error 'ERROR: "--entrypoint" requires a non-empty option argument.'
            fi
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

if [ -z "$IMAGE" ]; then
 IMAGE=DEFAULT_${FRAMEWORK^^}_IMAGE
 IMAGE=${!IMAGE}
fi

if [ -z "$NAME" ]; then
 NAME=$IMAGE
fi

}

show_options() {
       echo ""
       echo "Running Video Analytics Serving Image: '${IMAGE}'"
       echo "   Models: '${MODELS}'" 
       echo "   Pipelines: '${PIPELINES}'" 
       echo "   Framework: '${FRAMEWORK}'" 
       echo "   Environment: '${ENVIRONMENT}'" 
       echo "   Volume Mounts: '${VOLUME_MOUNT}'"
       echo "   Mode: '${MODE}'"
       echo "   Ports: '${PORTS}'"
       echo "   Name: '${NAME}'"
       echo "   Network: '${NETWORK}'"
       echo "   Entrypoint: '${ENTRYPOINT}'"
       echo "   User: '${USER}'"
       echo ""
}

show_help() {
  echo "usage: run.sh" 
  echo "  [--image image]"
  echo "  [--framework ffmpeg || gstreamer]"
  echo "  [--models path to model directory]" 
  echo "  [--pipelines path to pipelines directory]"
  echo "  [-v additional volume mount to pass to docker run]"
  echo "  [-e additional environment to pass to docker run"
  echo "  [-p additional ports to pass to docker run"
  echo "  [--network to pass to docker run"
  echo "  [--user to pass to docker run"
  exit 0
}

error() {
    printf '%s\n' "$1" >&2
    exit 
}

get_options "$@"

if [ "${MODE}" == "DEV" ]; then
  VOLUME_MOUNT+="-v $SOURCE_DIR:/home/video-analytics-serving/ "
  VOLUME_MOUNT+="-v /tmp:/tmp "
  VOLUME_MOUNT+="-v /dev:/dev "
  if [ -z "$NETWORK" ]; then
    NETWORK="--network=host"
  fi
  if [ -z "$ENTRYPOINT" ]; then
    ENTRYPOINT="--entrypoint /bin/bash"
  fi
  if [ -z "$MODELS" ]; then
    MODELS=$SOURCE_DIR/models
  fi
  if [ -z "$PIPELINES" ]; then
    PIPELINES=$SOURCE_DIR/pipelines/$FRAMEWORK
  fi  
  PRIVILEGED="--privileged "
elif [ "${MODE}" == "SERVICE" ]; then
  PORTS+="-p 8080:8080 "
  DEVICES+='-device /dev/dri '
else
 echo "Invalid Mode"
 show_help 
fi

if [ ! -z "$MODELS" ]; then
  VOLUME_MOUNT+="-v $MODELS:/home/video-analytics-serving/models "
fi
if [ ! -z "$PIPELINES" ]; then
  VOLUME_MOUNT+="-v $PIPELINES:/home/video-analytics-serving/pipelines "
fi


show_options

set -x
docker run -it --rm $ENVIRONMENT $VOLUME_MOUNT $NETWORK $PORTS $ENTRYPOINT --name ${NAME} ${PRIVILEGED} ${USER} $IMAGE
{ set +x; } 2>/dev/null
