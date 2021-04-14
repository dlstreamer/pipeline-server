#!/bin/bash
# This script runs the EdgeX VA Serving image with EdgeX sample pipeline 
# and dependencies.
RUN_PREFIX=
WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)
IMAGE_NAME=${IMAGE_NAME:-"edgex-video-analytics-serving:1.3.0"}
ENTRYPOINT_ARGS="--entrypoint-args \"--topic=objects_detected\" "
ENTRYPOINT_ARGS+="--entrypoint-args \"--source=https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\" "
ENTRYPOINT_ARGS+="--entrypoint-args \"--analytics-image=$IMAGE_NAME\" "

VOLUME_MOUNT=
PASS_THROUGH_PARAMS=

function show_help {
  echo "usage: ./run.sh"
  echo "  [ --dry-run : See the raw command(s) that will be executed by this script. ] "
  echo "  [ --generate : Passed to the entrypoint script located at ./edgex_bridge.py, instructing it to prepare EdgeX configuration to receive and process events triggered by VA Serving. ] "
  echo "  [ Remaining parameters pass through to VA Serving /docker/run.sh script ] "
}
#Get options passed into script, passing through parameters that target parent script.
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    --dev)
      # Handle this parameter locally to remove default/preceding entrypoint-args.
      # Allows user to successfully enter DEV mode.
      ENTRYPOINT_ARGS=""
      PASS_THROUGH_PARAMS+="--dev "
      shift
      ;;
    --dry-run)
      RUN_PREFIX=echo
      shift
      ;;
    --generate)
      VOLUME_MOUNT+="-v $SAMPLE_DIR:/home/video-analytics-serving/samples/edgex_bridge " \
      ENTRYPOINT_ARGS+="--entrypoint-args \"--generate\" "
      shift
      ;;
    *) # Default case: No more known options, so break out of the loop.
      PASS_THROUGH_PARAMS+=$@
      break ;;
  esac
done

$RUN_PREFIX $SAMPLE_DIR/../../docker/run.sh \
  --name edgex-vaserving \
  --image $IMAGE_NAME \
  $VOLUME_MOUNT \
  --user vaserving \
  --network host \
  $ENTRYPOINT_ARGS \
  $PASS_THROUGH_PARAMS
