#!/bin/bash

# This script invokes docker-compose to launch EdgeX microservices,
# including the edgex-dlstreamer-pipeline-server container.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
COMPOSE_PATH=$SCRIPT_DIR/edgex
COMPOSE_FILE=$COMPOSE_PATH/docker-compose.override.yml
RTSP_CLIENT=

show_help() {
  echo "usage: ./start_edgex.sh"
  echo "  [--rtsp-path  path for rtsp uri]   (default: edgex_event_emitter)"
  echo "  [--rtsp-client  vlc || ffplay]   (default: manually connect)"
  exit 0
}

error() {
    printf '%s %s\n' "$1" "$2" >&2
    exit 1
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
    -h | -\? | --help)
        show_help # Display a usage synopsis.
        exit
        ;;
    --rtsp-path)
        if [ "$2" ]; then
            RTSP_PATH=$2
            shift
        else
            error 'ERROR: "--rtsp-path" requires an argument.'
        fi
        ;;
    --rtsp-client)
        if [ "$2" ]; then
            RTSP_CLIENT=$2
            shift
        else
            error 'ERROR: "--rtsp-client" requires an argument.'
        fi
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
    *) # Default case: No more options, so break out of the loop.
        break ;;
    esac

    shift
done

# Convenience function to launch optional RTSP client for viewing
# VA Serving's processed pipeline frames.
function rtsp_connect {
    ON_SUCCESS_MESSAGE=0
    ON_USER_TERMINATED=130
    set +o pipefail
    echo "RTSP Client will establish connection to display $DISPLAY"
    for rtsp_connect in {1..10}
    do
        echo $(printf '=%.0s' {1..70})
        echo "Attempt $rtsp_connect connecting to pipeline RTSP frames..."
        case "$RTSP_CLIENT" in
            "ffplay")
                # https://ffmpeg.org/ffplay.html
                RENDER_MATCH_MESSAGE="from '$PIPELINE_RENDER_PATH'"
                echo "Monitoring ffplay for success indicator message..."
                ffplay -autoexit -window_title "${edgex_sample_title}" \
                    $PIPELINE_RENDER_PATH 2>&1 >/dev/null | grep "$RENDER_MATCH_MESSAGE"
                ;;
            "vlc")
                # https://www.commandlinux.com/man-page/man1/cvlc.1.html
                RENDER_MATCH_MESSAGE="Failed to connect with $PIPELINE_RENDER_PATH\|X server failure\|cvlc: command not found"
                echo "Monitoring vlc for failure indicator message..."
                ON_SUCCESS_MESSAGE=1
                # X server failure explanation:
                # https://gitlab.freedesktop.org/mesa/mesa/-/issues/116
                cvlc --play-and-exit --one-instance --meta-title="$edgex_sample_title" \
                    $PIPELINE_RENDER_PATH 2>&1 >/dev/null | grep "$RENDER_MATCH_MESSAGE"
                ;;
        esac
        PIPE_STATUS=( "${PIPESTATUS[@]}" )
        if [ "${PIPE_STATUS[1]}" == "$ON_SUCCESS_MESSAGE" ]; then
            echo "Played content with watermarks";
            break;
        elif [ "${PIPE_STATUS[1]}" == "$ON_USER_TERMINATED" ]; then
            echo "User intentionally exited";
            break;
        else
            echo "No RTSP broadcast detected. Re-attempting..." ;
            sleep 1
            continue
        fi
    done
}

function confirm_client_exists {
    if ! [ -x "$(command -v $RTSP_CLIENT)" ]; then
        echo "Error: $RTSP_CLIENT is not installed." >&2
        exit 1
    fi
}

# Prepare RTSP Client connection configuration
export edgex_env_enable_rtsp=false
export edgex_rtsp_host=rtsp://127.0.0.1
export edgex_rtsp_port=8554
export edgex_default_display=:0.0
export edgex_default_rtsp_path="edgex_event_emitter"
export edgex_sample_title="VA Serving - EdgeX Sample"
export edgex_request_rtsp_path=""

if [[ ! -z "$RTSP_PATH" ]]; then
    export edgex_env_enable_rtsp=true
    export edgex_rtsp_path=$RTSP_PATH
else
    export edgex_rtsp_path=$edgex_default_rtsp_path
fi
PIPELINE_RENDER_PATH=$edgex_rtsp_host:$edgex_rtsp_port/$edgex_rtsp_path

if [[ ! -z "$RTSP_CLIENT" ]]; then
    export edgex_env_enable_rtsp=true
    if [ $RTSP_CLIENT != 'vlc' ] && [ $RTSP_CLIENT != 'ffplay' ]; then
        echo "Invalid RTSP_CLIENT"
        show_help
    fi
    if [ "$DISPLAY" == "" ]; then DISPLAY=$edgex_default_display; fi
    export edgex_sample_title+=" ($RTSP_CLIENT)"
    confirm_client_exists
else
    if [[ ! -z "$RTSP_PATH" ]]; then
        echo $(printf '=%.0s' {1..70})
        echo "Connect your RTSP client to: $PIPELINE_RENDER_PATH"
        echo $(printf '=%.0s' {1..70})
    fi
fi

if [ "$edgex_env_enable_rtsp" == "true" ]; then
    export edgex_request_rtsp_path="--rtsp-path $edgex_rtsp_path"
fi

# Launch EdgeX Stack and another VA Serving pipeline instance (if input media stream has completed)
if test -f "$COMPOSE_FILE"; then
    cd $COMPOSE_PATH
    docker-compose up -d
    if [[ ! -z "$RTSP_CLIENT" ]]; then
        rtsp_connect $edgex_rtsp_port $edgex_rtsp_path
    fi
else
    echo "ERROR! You must first successfully run ./fetch_edgex.sh and ./build.sh"
fi
