#!/bin/bash -e
#
# Copyright (C) 2019-2020 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#

RUN_PREFIX=
MODELS=
PIPELINES=
FRAMEWORK=
IMAGE=
VOLUME_MOUNT=
MODE=SERVICE
PORTS=
DEVICES=
DEFAULT_GSTREAMER_IMAGE="dlstreamer-pipeline-server-gstreamer"
DEFAULT_FFMPEG_IMAGE="dlstreamer-pipeline-server-ffmpeg"
ENTRYPOINT=
ENTRYPOINT_ARGS=
PRIVILEGED=
NETWORK=
USER=
INTERACTIVE=-it
DEVICE_CGROUP_RULE=
USER_GROUPS=
ENABLE_RTSP=${ENABLE_RTSP:-"false"}
ENABLE_WEBRTC=${ENABLE_WEBRTC:-"false"}
RTSP_PORT=8554

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
SOURCE_DIR=$(dirname $SCRIPT_DIR)
ENVIRONMENT=$(env | cut -f1 -d= | grep -E '_(proxy)$' | sed 's/^/-e / ' | tr '\n' ' ')

show_options() {
    echo ""
    echo "Running Pipeline Server Image: '${IMAGE}'"
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
    echo "   EntrypointArgs: '${ENTRYPOINT_ARGS}'"
    echo "   User: '${USER}'"
    echo "   User Groups: '${USER_GROUPS}'"
    echo "   Devices: '${DEVICES}'"
    echo "   Device CGroup Rule: '${DEVICE_CGROUP_RULE}'"
    echo ""
}

show_help() {
  echo "usage: run.sh"
  echo "  [--image image]"
  echo "  [--framework ffmpeg || gstreamer]"
  echo "  [--models path to models directory]"
  echo "  [--pipelines path to pipelines directory]"
  echo "  [-v additional volume mount to pass to docker run]"
  echo "  [-e additional environment to pass to docker run]"
  echo "  [--entrypoint-args additional parameters to pass to entrypoint in docker run]"
  echo "  [-p additional ports to pass to docker run]"
  echo "  [--network name network to pass to docker run]"
  echo "  [--user name of user to pass to docker run]"
  echo "  [--group-add name of user group to pass to docker run]"
  echo "  [--name container name to pass to docker run]"
  echo "  [--device device to pass to docker run]"
  echo "  [--enable-rtsp To enable rtsp re-streaming]"
  echo "  [--rtsp-port Specify the port to use for rtsp re-streaming]"
  echo "  [--enable-webrtc To enable WebRTC frame destination]"
  echo "  [--dev run in developer mode]"
  exit 0
}

error() {
    printf '%s\n' "$1" >&2
    exit
}

enable_hardware_access() {
    # GPU
    if ls /dev/dri/render* 1> /dev/null 2>&1; then
        echo "Found /dev/dri/render entry - enabling for GPU"
        DEVICES+='--device /dev/dri '
        RENDER_GROUPS=$(stat -c '%g' /dev/dri/render*)
        for group in $RENDER_GROUPS
        do
            USER_GROUPS+="--group-add $group "
        done
    fi

    # Intel(R) NCS2
    if [ -d /dev/bus/usb ]; then
        echo "Found /dev/bus/usb - enabling for Intel(R) NCS2"
        DEVICE_CGROUP_RULE=--device-cgroup-rule=\'c\ 189:*\ rmw\'
        VOLUME_MOUNT+="-v /dev/bus/usb:/dev/bus/usb "
    fi

    # HDDL
    if compgen -G /dev/myriad* > /dev/null ; then
        echo "Found /dev/myriad devices - enabling for HDDL-R"
        VOLUME_MOUNT+="-v /var/tmp:/var/tmp -v /dev/shm:/dev/shm "
    fi

    # Webcam
    for device in $(ls /dev | grep video); do
        echo "Found /dev/$device - enabling webcam"
        DEVICES+="--device /dev/$device "
    done

    # Microphone
    if [ -e /dev/snd ]; then
        echo "Found /dev/snd - enabling microphone"
        DEVICES+="--device /dev/snd "
    fi
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | -\? | --help)
        show_help # Display a usage synopsis.
        exit
        ;;
    --dry-run)
        RUN_PREFIX=echo
        ;;
    --image) # Takes an option argument; ensure it has been specified.
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
            error 'ERROR: "--user" requires a non-empty option argument.'
        fi
        ;;
    --group-add)
        if [ "$2" ]; then
            USER_GROUPS+="--group-add $2 "
            shift
        else
            error 'ERROR: "--group-add" requires a non-empty option argument.'
        fi
        ;;
    --device)
        if [ "$2" ]; then
            DEVICES+="--device $2 "
            shift
        else
            error 'ERROR: "--device" requires a non-empty option argument.'
        fi
        ;;
    --privileged)
        PRIVILEGED="--privileged "
        ;;
    --device-cgroup-rule)
        if [ "$2" ]; then
            DEVICE_CGROUP_RULE="--device-cgroup-rule=$2 "
            shift
        else
            error 'ERROR: "--device-cgroup-rule" requires a non-empty option argument.'
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
    --entrypoint-args)
        if [ "$2" ]; then
            ENTRYPOINT_ARGS+="$2 "
            shift
        else
            error 'ERROR: "--entrypoint-args" requires a non-empty option argument.'
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
    --rtsp-port)
        if [ "$2" ]; then
            RTSP_PORT=$2
            shift
        else
            error 'ERROR: "--rtsp-port" requires a non-empty option argument.'
        fi
        ;;
    --enable-rtsp)
        ENABLE_RTSP=true
        ;;
    --enable-webrtc)
        ENABLE_WEBRTC=true
        ;;
    --non-interactive)
        unset INTERACTIVE
        ;;
    --) # End of all options.
        shift
        break
        ;;
    -?*)
        printf 'WARN: Unknown option (ignored): %s\n' "$1" >&2
        ;;
    *) # Default case: No more options, so break out of the loop.
        break ;;
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
    # Convert tag separator if exists
    NAME=${IMAGE//[\:\/]/_}
fi

if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $SOURCE_DIR:/home/pipeline-server/ "
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
elif [ ! -z "$ENTRYPOINT" ]; then
    MODE=CUSTOM_ENTRYPOINT
elif [ "${MODE}" == "SERVICE" ]; then
    if [ -z "$PORTS" ]; then
        PORTS+="-p 8080:8080 "
    fi
else
    echo "Invalid Mode"
    show_help
fi

enable_hardware_access

if [ "$ENABLE_RTSP" != "false" ]; then
    ENVIRONMENT+="-e ENABLE_RTSP=$ENABLE_RTSP -e RTSP_PORT=$RTSP_PORT "
    PORTS+="-p $RTSP_PORT:$RTSP_PORT "
fi

if [ "$ENABLE_WEBRTC" != "false" ]; then
    ENVIRONMENT+="-e ENABLE_WEBRTC=$ENABLE_WEBRTC "
fi

if [ ! -z "$MODELS" ]; then
    VOLUME_MOUNT+="-v $MODELS:/home/pipeline-server/models "
fi

if [ ! -z "$PIPELINES" ]; then
    VOLUME_MOUNT+="-v $PIPELINES:/home/pipeline-server/pipelines "
fi

if [ ! -z "$VOLUME_MOUNT" ]; then
    if [ -z "$USER" ]; then
        USER="--user $UID"
    fi
fi

if [ ! -z "$USER" ]; then
    for group in "audio" "users"
    do
        USER_GROUPS+="--group-add $group "
    done
fi

show_options

# eval must be used to ensure the --device-cgroup-rule string is correctly parsed
eval "$RUN_PREFIX docker run $INTERACTIVE --rm $ENVIRONMENT $VOLUME_MOUNT $DEVICE_CGROUP_RULE $DEVICES $NETWORK $PORTS $ENTRYPOINT --name ${NAME} ${PRIVILEGED} ${USER} $USER_GROUPS $IMAGE ${ENTRYPOINT_ARGS}"
