#!/bin/bash -e

WORK_DIR=$(dirname $(readlink -f "$0"))
SAMPLE_DIR=$(dirname $WORK_DIR)

SAMPLE_BUILD_ARGS=$(env | cut -f1 -d= | grep -E '_(proxy|REPO|VER)$' | sed 's/^/--build-arg / ' | tr '\n' ' ')
PIPELINES="pipelines"
MODELS="models_list/models.list.yml"
BASE_IMAGE=
OMZ_VERSION=
# Name the image we will build and add to EdgeX Foundry startup
TAG_BASE="dlstreamer-pipeline-server-edgex-base:latest"
TAG="dlstreamer-pipeline-server-edgex:latest"

#Get options passed into script, passing through parameters supported by the parent build script.
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -h | -\? | --help)
      show_help
      exit
      ;;
    --tag)
      if [ "$2" ]; then
        TAG=$2
        shift
      else
        error 'ERROR: "--tag" requires an argument.'
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
    --models)
      if [ "$2" ]; then
        MODELS=$2
        shift
      else
        error 'ERROR: "--models" requires an argument.'
      fi
      ;;
    *) # Default case: No more known options, so break out of the loop.
      PASS_THROUGH_PARAMS=$@
      break ;;
  esac
  shift
done

function show_help {
  echo "usage: ./build.sh"
  echo "  [ --models : Path to model list YAML file, must be a relative path. Allows caller to specify which models to persist into the resulting Docker image. ] "
  echo "  [ --pipelines : Path to pipelines, must be a relative path. Allows caller to specify which pipelines to persist into the resulting Docker image. ] "
  echo "  [ --tag : Alternate name and/or tag for the resulting image. This may be unique for your chosen set of pipelines and/or models. ] "
}
# The specific Pipeline(s) and Model(s) these are copied in directly within Dockerfile

function launch { echo $@
    $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        exit $exit_code
    fi
    return $exit_code
}

# Build Intel(R) DL Streamer Pipeline Server
launch "$SAMPLE_DIR/../../docker/build.sh
  --framework gstreamer
  --create-service true $BASE_IMAGE $OMZ_VERSION
  --models $SAMPLE_DIR/$MODELS
  --pipelines samples/edgex_bridge/$PIPELINES
  --tag $TAG_BASE
  $PASS_THROUGH_PARAMS"

# Build EdgeX Bridge Extension and override entrypoint defined by FINAL_STAGE
# in Intel(R) DL Streamer Pipeline Server parent image Dockerfile
launch "docker build -f $WORK_DIR/Dockerfile $SAMPLE_BUILD_ARGS
  --build-arg BASE=$TAG_BASE
  $PASS_THROUGH_PARAMS -t $TAG $SAMPLE_DIR "
export IMAGE_NAME=$TAG

# Generate configurations needed by EdgeX for integration. This includes all of the
# necessary runtime characteristics of our edgex-video-analytics microservice, topic to emit events on, and
# mapping to edgex-device-mqtt microservice.
# To perform this we will invoke the entrypoint edgex_bridge.py with a --generate parameter, instructing
# to output configuration to your host through a volume mount accessible by your current user id.
echo "."
echo "Launching post-build step to generate configurations needed to integrate with EdgeX Foundry."
launch "$SAMPLE_DIR/docker/run.sh --generate --user $UID"
