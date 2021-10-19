#!/bin/bash -e

CURRENT_DIR=$(dirname "$(readlink -f "$0")")
ROOT_DIR=$(dirname $CURRENT_DIR)

RUN_PREFIX=
IMAGE=video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension
VOLUME_MOUNT=" -v /tmp:/tmp -v /dev/shm:/dev/shm "
DOCKER_DIR=/home/edge-ai-extension
MODE=SERVICE
PORTS=
DEVICES=
ENTRYPOINT=
ENTRYPOINT_ARGS=
PRIVILEGED=
NETWORK=
USER=
INTERACTIVE=-it
DEVICE_CGROUP_RULE=
USER_GROUPS=
ENABLE_RTSP=
RTSP_PORT=8554
ENVIRONMENT=$(env | cut -f1 -d= | grep -E '_(proxy)$' | sed 's/^/-e / ' | tr '\n' ' ')

show_options() {
    echo ""
    echo "Running Image: '${IMAGE}'"
    echo "   Environment: '${ENVIRONMENT}'"
    echo "   Volume Mounts: '${VOLUME_MOUNT}'"
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
  echo "usage: ./run_server.sh"
  echo "  [--image image]"
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
  echo "  [--dev run in developer mode by mounting local source code]"
  echo ""
  echo "**Application**"
  echo ""
  ENTRYPOINT_ARGS+="--help "
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
        USER_GROUPS+="--group-add $(stat -c '%g' /dev/dri/render*) "
    fi

    # Intel(R) NCS2
    if [ -d /dev/bus/usb ]; then
        echo "Found /dev/bus/usb - enabling for Intel(R) NCS2"
        DEVICE_CGROUP_RULE=--device-cgroup-rule=\'c\ 189:*\ rmw\'
        VOLUME_MOUNT+="-v /dev/bus/usb:/dev/bus/usb "
    fi
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | -\? | --help)
        show_help # Display a usage synopsis.
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
    --non-interactive)
        unset INTERACTIVE
        ;;
    --) # End of all options.
        shift
        break
        ;;
    *)
      ENTRYPOINT_ARGS+=" $1 "
      ;;
    esac

    shift
done

if [ -z "$NAME" ]; then
    # Convert tag separator if exists
    NAME=${IMAGE//[\:\/]/_}
fi

if [ "${MODE}" == "DEV" ]; then
    VOLUME_MOUNT+="-v $ROOT_DIR:$DOCKER_DIR "
    VOLUME_MOUNT+="-v /dev:/dev "
    if [ -z "$NETWORK" ]; then
        NETWORK="--network=host"
    fi
    PRIVILEGED="--privileged "
elif [ "${MODE}" == "SERVICE" ]; then
    if [ -z "$PORTS" ]; then
        PORTS+="-p 5001:5001 "
    fi
else
    echo "Invalid Mode"
    show_help
fi
enable_hardware_access

if [ ! -z "$PIPELINE_NAME" ]; then
  ENVIRONMENT+="-e PIPELINE_NAME=$PIPELINE_NAME "
fi

if [ ! -z "$PIPELINE_VERSION" ]; then
  ENVIRONMENT+="-e PIPELINE_VERSION=$PIPELINE_VERSION "
fi

if [ ! -z "$DEBUG_PIPELINE" ]; then
  ENVIRONMENT+="-e DEBUG_PIPELINE=$DEBUG_PIPELINE "
fi

if [ ! -z "$GST_DEBUG" ]; then
  ENVIRONMENT+="-e GST_DEBUG=$GST_DEBUG "
fi

if [ ! -z "$ENABLE_RTSP" ]; then
    ENVIRONMENT+="-e ENABLE_RTSP=true -e RTSP_PORT=$RTSP_PORT "
    PORTS+="-p $RTSP_PORT:$RTSP_PORT "
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