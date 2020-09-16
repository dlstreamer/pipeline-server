# Overview - Model Download Tool

VA Serving pipelines exclusively use models in the OpenVINO Intermediate Representation (IR) format.
Intel maintains a set of ready to use models in the OpenVINO Open Model Zoo (OMZ).
The Model Download Tool improves developer experience by automatically downloading and converting specified models from OMZ. The tool also downloads model-proc files available from DL Streamer repo and lays out files in correct directory structure compatible with VA Serving.

## How to use
The tool assumes that OpenVINO is installed and environment is set up. If your host is set up, you can run the tool from the host. Otherwise you can run
the tool while in developer mode in Docker (`./docker/run.sh --dev`).

The tool will download models from Open Model Zoo(OMZ), so it will need network access.

The tool accepts as input argument a yaml file that will have the model info in it. The yaml file can provide model name and the downloader will get all the model precisions from OMZ.
If no input file given, by default the tool looks for a `models.list.yml` file inside the model_downloader folder. This file will list a model name, alias, version and precision. Alias, version and precision are optional. If none provided, the default values for these would be:
* alias = model name
* version = 1
* precision = all available precisions

A simple yaml input file will look like:
```yaml
- mobilenet-ssd
- emotions-recognition-retail-0003
```
An example of a detailed yaml entry would be:
```yaml
- model: yolo-v3-tf
  alias: object_detection
  version: 2
  precision: [FP32,INT8]
```
The yaml input file can contain a combination of simple as well as detailed entries.  

The tool also downloads the model-proc file from DL streamer repo. The model-proc file must have the same name as the model being downloaded.

## How to run
Run the tool without any arguments:  
This will get the model names by default from the input yaml file `models.list.yml` in the model_downloader folder, create a `models` folder and download the models into it. 
```bash
$ python3 model_downloader
```
This `models` directory can then be moved over to the root folder to use with VA Serving.

### Options
Some of the options you can provide while running the tool include:

[ --model-list : Specify a different models.list.yml file than the default ]

[ --output-dir : Specify directory to create model folder ]

[ --force : Specify if download needs to be forced ]