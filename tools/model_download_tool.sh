#!/bin/bash

#For the rest of the script treat the location of the script as the root folder
cd $(dirname $0)

#Default variables
USE_SPECIFIC_MODEL_FROM_CMD=false
USE_SPECIFIC_MODEL_FROM_CSV=false
LIST_OF_SPECIFIC_MODELS_FROM_CMD=()
LIST_OF_SPECIFIC_MODELS_FROM_CSV=()
MODEL_LIST_FILE=models.csv
MODEL_PROC_PATH=model_procs
OUTPUT_DIR=models
QUIET=false

#Set the path to the model optimizer
if [ -d "/opt/intel/dldt" ] ; then \
  MO_PATH=/opt/intel/dldt/model-optimizer/mo.py ; \
else \
  MO_PATH=/opt/intel/openvino/deployment_tools/model_optimizer/mo.py ; \
fi

#Model is coming from OpenModelZoo
function download_model_from_open_model_zoo {
  #$1 is model name
  #$2 is alias
  #$3 is version
  #Assume that these values are set by the caller, empty check not needed
  model_name=$1
  model_alias=$2
  version=$3

  if ! $QUIET; then
    echo "Downloading $model_name to $model_alias/$version using OpenModelZoo tools"
  fi

  #Set the path to OpenModelZoo
  if [ -d "/opt/intel/dldt" ] ; then \
    open_model_zoo_path=/opt/intel/dldt/open_model_zoo ; \
  else \
    open_model_zoo_path=/opt/intel/openvino/deployment_tools/open_model_zoo ; \
  fi

  #Download and convert the model
  if $QUIET; then
    ${open_model_zoo_path}/tools/downloader/downloader.py --name $model_name > /dev/null 2>&1
    ${open_model_zoo_path}/tools/downloader/converter.py --name $model_name --mo $MO_PATH > /dev/null 2>&1
  else
    ${open_model_zoo_path}/tools/downloader/downloader.py --name $model_name
    ${open_model_zoo_path}/tools/downloader/converter.py --name $model_name --mo $MO_PATH
  fi

  #copy over the model precision folders to the appropriate directory expected by VA-Serving
  mkdir -p $OUTPUT_DIR/$model_alias/$version
  
  #Grab the model from the public or intel folder and move it to the models folder
  if [ -d "./public/$model_name" ] ;
  then
    for d in ./public/$model_name/*/ ; do
      cp -r $d/ $OUTPUT_DIR/$model_alias/$version
    done
  fi
  if [ -d "./intel/$model_name" ] ;
  then
    for d in ./intel/$model_name/*/ ; do
      cp -r $d/ $OUTPUT_DIR/$model_alias/$version
    done
  fi
}

#Helper function to download the model and copy over model-proc if available
#Designed to be easily extendable in the future for non-OpenModelZoo sources
function download_model {
  #$1 is model name
  #$2 is alias
  #$3 is version
  model_name=$1
  model_alias=$2
  version=$3

  #If version not provided, set version to 1
  if [ -z "$version" ] ;
  then
    version=1
  fi

  #Check if model has already been downloaded. If yes, skip
  if [ -d "./models/$model_alias/$version" ] ;
  then
    echo "Skipping download of $model_name, $model_alias/$version directory already exists"
    return
  fi

  #Download the model from OpenModelZoo
  download_model_from_open_model_zoo $model_name $model_alias $version

  #if Model Proc is available, copy over to model directory
  #otherwise touch the file (required for VA-Serving to load the model)
  if [ -f $MODEL_PROC_PATH/$model_name.json ] ;
  then
    cp $MODEL_PROC_PATH/$model_name.json $OUTPUT_DIR/$model_alias/$version
  else
    #Check to see if gst-video-analytics has a model proc
    wget -q https://raw.githubusercontent.com/opencv/gst-video-analytics/preview/audio-detect/samples/model_proc/$model_name.json
    if [ $? -eq 0 ] ;
    then
      if ! $QUIET; then
        echo "Downloaded $model_name model-proc file from gst-video-analytics repo"
      fi
      mv $model_name.json $OUTPUT_DIR/$model_alias/$version/
    else
      echo "Warning, model-proc not found in gst-video-analytics repo."
      echo "Creating empty json file for $model_alias/$version to allow model to load in VA-Serving"
      echo "Do not specify model-proc in pipeline that utilizes this model"
      touch $OUTPUT_DIR/$model_alias/$version/$model_name.json
    fi
  fi

  unset model_name
  unset model_alias
  unset version
}

#Get options passed into script
function get_options {
  while :; do
    case $1 in
      -h | -\? | --help)
        show_help
        exit
        ;;
      --specific-model-from-csv)
        if [ "$2" ]; then
          USE_SPECIFIC_MODEL_FROM_CSV=true
          LIST_OF_SPECIFIC_MODELS_FROM_CSV+=($2)
	  shift
        else
          error 'ERROR: "--specific-model" requires a non-empty option argument.'
        fi
        ;;
      --specific-model)
        if [ "$2" ]; then
          USE_SPECIFIC_MODEL_FROM_CMD=true
          LIST_OF_SPECIFIC_MODELS_FROM_CMD+=($2)
          shift
        else
          error 'ERROR: "--specific-model" requires a non-empty option argument.'
        fi
        ;;
      --model-list)
        if [ "$2" ]; then
          MODEL_LIST_FILE=$2
          shift
        else
          error 'ERROR: "--model-file" requires a non-empty option argument.'
        fi
        ;;
      --model-proc-path)
        if [ "$2" ]; then
          MODEL_PROC_PATH=$2
          shift
        else
          error 'ERROR: "--model-proc-path" requires a non-empty option argument.'
        fi
        ;;
      --output-dir)
        if [ "$2" ]; then
          OUTPUT_DIR=$2/models
          shift
        else
          error 'ERROR: "--output-dir" requires a non-empty option argument.'
        fi
        ;;
      --quiet)
        QUIET=true
        ;;
      *)
        break
        ;;
    esac

    shift
  done
}

function show_help {
  echo "usage: model_download_tool.sh"
  echo "  [ --specific-model : specify a model,alias,version directly in the command line to download/convert instead of using a csv file ]"
  echo "  [ --specific-model-from-csv : specify a specific model from the model.csv to download/convert instead of everything ]"
  echo "  [ --model-list : Specify a different model.csv file than the default ]"
  echo "  [ --model-proc-path : Specify a path to a folder containing model procs. Default is current directory ]"
  echo "  [ --output-dir : Specify directory to create model folder ]"
  echo "  [ --quiet : Will run tool quietly except for errors ]"
}

function error {
    printf '%s\n' "$1" >&2
    exit
}


#Get options and set variables
get_options "$@"

#Create models directory if it doesn't exist
mkdir -p $OUTPUT_DIR

#For each model, provide the download_model script the name, alias, and version from the model list file
if $USE_SPECIFIC_MODEL_FROM_CMD; then
  for model_line in "${LIST_OF_SPECIFIC_MODELS_FROM_CMD[@]}"; do
    OLDIFS=$IFS
    IFS=","
    read -r -a model_array <<< "$model_line"
    model_name="${model_array[0]}"
    model_alias="${model_array[1]}"
    version="${model_array[2]}"
    if [ -z "$model_alias" ] ;
    then
      model_alias=$model_name
    fi

    download_model $model_name $model_alias $version
    unset model_array
    IFS=$OLDIFS
  done
elif $USE_SPECIFIC_MODEL_FROM_CSV; then
  for model in "${LIST_OF_SPECIFIC_MODELS_FROM_CSV[@]}"; do
    OLDIFS=$IFS
    IFS=","
    while read model_name model_alias version
    do
      if [ $model == $model_name ] ;
      then
        if [ -z "$model_alias" ] ;
        then
          model_alias=$model_name
        fi

        download_model $model_name $model_alias $version
        break
      fi
    done < $MODEL_LIST_FILE
    IFS=$OLDIFS
  done
else
  OLDIFS=$IFS
  IFS=","
  while read model_name model_alias version
  do
    if [ -z "$model_alias" ] ;
    then
      model_alias=$model_name
    fi

    download_model $model_name $model_alias $version
  done < $MODEL_LIST_FILE
  IFS=$OLDIFS
fi

#clean up downloaded models
rm -rf ./intel/ ./public/
