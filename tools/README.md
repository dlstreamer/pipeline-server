# Getting Started with the Model Download Tool

The Model Download Tool is designed to abstract away the model directory
structure and make it easy to integrate your own specified models into
VA-Serving

The script will parse through a list of model names, download and
convert the models, and generate a models directory that can be placed in
VA-Serving

## How to use
The script assumes OpenVINO is installed and environment is set up. If your
host is set up, you can run the script from the host. Otherwise you can run
the script while in developer mode in Docker (./docker/run.sh --dev)

The script will download models from OpenModelZoo, so it will need network access

The script looks for a model.csv file alongside the script. This file will list
on each line a model name, alias (optional), and version (optional).

If you have created a model-proc json file for the model you wish to use,
place the file in a model-proc directory that exists alongside the script.
The model-proc file must have the same name as the model being downloaded

Once ready, run the script
`./model_download_tool.sh`

A model directory will be created next to the script, which can be moved over
to the root folder to use with VA-Serving

### How to download specific models only
The script supports an optional `--specific-model` parameter that can be used 
to download a specific model instead of everything in the model list file.
This parameter can be repeated for each specific model

### Options
 [ --specific-model : specify specific model from the model.csv to download/convert instead of everything ]

 [ --model-list : Specify a different model.csv file than the default ]

 [ --model-proc-path : Specify a path to a folder containing model procs. Default is current directory of the script ]

 [ --output-dir : Specify directory to create model folder ]

 [ --quiet : Will run tool quietly except for errors ]
