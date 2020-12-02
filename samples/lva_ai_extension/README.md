# OpenVINO™ DL Streamer – Edge AI Extension Module

| [Getting Started](#getting-started) | [Edge AI Extension Module Options](#edge-ai-extension-module-options) | [Additional Examples](#additional-standalone-edge-ai-extension-examples) | [Test Client](#test-client) |
[Changing Models](#updating-or-changing-detection-and-classification-models)

The OpenVINO™ DL Streamer - Edge AI Extension module is a microservice based on [Video Analytics Serving](/README.md) that provides video analytics pipelines built with OpenVINO™ DL Streamer. Developers can send decoded video frames to the AI Extension module which performs detection, classification, or tracking and returns the results. The AI Extension module exposes gRPC APIs that are compatible with [Live Video Analytics on IoT Edge](https://azure.microsoft.com/en-us/services/media-services/live-video-analytics/). Powered by OpenVINO™ toolkit, the AI Extension module enables developers to build, optimize and deploy deep learning inference workloads for maximum performance across Intel® architectures.

## Highlights:

- Scalable, high-performance solution for serving video analytics pipelines on Intel® architectures
- Pre-loaded Object Detection, Object Classification and Object Tracking pipelines to get started quickly
- Pre-loaded [person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/intel/person-vehicle-bike-detection-crossroad-0078/description/person-vehicle-bike-detection-crossroad-0078.md) and [vehicle-attributes-recognition-barrier-0039](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/intel/vehicle-attributes-recognition-barrier-0039/description/vehicle-attributes-recognition-barrier-0039.md) models.
- gRPC API enabling fast data transfer rate and low latency
- Validated support for [Live Video Analytics on IoT Edge](https://azure.microsoft.com/en-us/services/media-services/live-video-analytics/).
- Supported Configuration: Pre-built Ubuntu Linux container for CPU and iGPU

# Getting Started

The OpenVINO™ DL Streamer - Edge AI Extension module is available as a pre-built docker image. The image can run as a standalone microservice or as a module within an Live Video Analytics graph. For more information on deploying the module as part of a Live Video Analytics graph please see [Configuring the AI Extension Module for Live Video Analytics](#configuring-the-ai-extension-module-for-live-video-analytics) and refer to the [Live Video Analytics documentation](https://azure.microsoft.com/en-us/services/media-services/live-video-analytics/). The following instructions demonstrate running the microservice and test client outside of Live Video Analytics.

## Pulling the Image from Docker Hub

Pull the pre-built image using the following command.
You will need to tag the image in order to use it with the docker run scripts described in subsequent sections.

```
$ docker pull intel/video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension
$ docker tag intel/video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension \
     video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension
```

For instructions on building your own image please see [Building an Edge AI Extension Module Image](#building-an-edge-ai-extension-module-image).

## Running the Edge AI Extension Module

To run the module as a standalone microservice with an `object_detection` pipeline use the `run_server.sh` script with default options. For examples of additional options see [Additional Standalone Edge AI Extension Examples](#additional-standalone-edge-ai-extension-examples).

```bash
$ ./docker/run_server.sh
<snip>
Starting Protocol Server Application on port 5001
```

## Sending a Test Frame for Object Detection

To send a test frame to the microservice and receive `object_detection` results use the `run_client.sh` script.

```bash
$ ./docker/run_client.sh
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: Options for __main__.py
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: grpc_server_address == 127.0.0.1:5001
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: sample_file == /home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,817] [MainThread  ] [INFO]: loop_count == 1
[AIXC] [2020-11-20 23:29:10,818] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,818] [MainThread  ] [INFO]: use_shared_memory == False
[AIXC] [2020-11-20 23:29:10,818] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,818] [MainThread  ] [INFO]: output_file == /tmp/results.jsonl
[AIXC] [2020-11-20 23:29:10,818] [MainThread  ] [INFO]: =======================
[AIXC] [2020-11-20 23:29:10,842] [Thread-2    ] [INFO]: MediaStreamDescriptor request #1
[AIXC] [2020-11-20 23:29:10,842] [Thread-2    ] [INFO]: MediaSample request #2
[AIXC] [2020-11-20 23:29:10,843] [MainThread  ] [INFO]: [Received] AckNum: 1
[AIXC] [2020-11-20 23:29:10,849] [Thread-2    ] [INFO]: MediaSample request #3
[AIXC] [2020-11-20 23:29:11,417] [Thread-3    ] [INFO]: [Received] AckNum: 2
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: Inference result 2
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (1.00) [0.30, 0.47, 0.09, 0.39]
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (0.97) [0.36, 0.40, 0.05, 0.24]
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (0.94) [0.44, 0.42, 0.08, 0.43]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.92) [0.57, 0.38, 0.05, 0.25]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.91) [0.69, 0.56, 0.12, 0.43]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.90) [0.68, 0.42, 0.04, 0.24]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.82) [0.64, 0.36, 0.05, 0.27]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.60) [0.84, 0.44, 0.05, 0.29]
[AIXC] [2020-11-20 23:29:11,422] [MainThread  ] [INFO]: Client finished execution
```

# Edge AI Extension Module Options

The module can be configured using command line options or environment variables (command line options take precedence).

| Setting             | Command line option | Environment variable | Default value    |
|---------------------|---------------------|----------------------|------------------|
| gRPC port           | -p                  | PORT                 | 5001             |
| Pipeline name       | --pipeline-name     | PIPELINE_NAME        | object_detection |
| Pipeline version    | --pipeline-version  | PIPELINE_VERSION     | person_vehicle_bike_detection |
| Pipeline parameters | --parameters        | PARAMETERS           | {}                |
| Use debug pipeline  | --debug             | DEBUG_PIPELINE       |                   |

## Video Analytics Pipelines

The following pipelines are included in the AI Extension:

| Pipeline Name  | Pipeline Version | Pipeline Definition
| ------------- | ------------- | --------------- |
| object_detection | person_vehicle_bike_detection  | [definition](/samples/lva_ai_extension/pipelines/object_detection/person_vehicle_bike_detection/pipeline.json)
| object_classification  | vehicle_attributes_recognition  | [definition](/samples/lva_ai_extension/pipelines/object_classification/vehicle_attributes_recognition/pipeline.json)
| object_tracking  | person_vehicle_bike_tracking  | [definition](/samples/lva_ai_extension/pipelines/object_tracking/person_vehicle_bike_tracking/pipeline.json)

## Configuring the AI Extension Module for Live Video Analytics

Update the [deployment manifest](/samples/lva_ai_extension/deployment/deployment.grpc.template.json) template located in the deployment folder:
* Make sure that the 'lvaExtension'->'image' property shows the URI of the OpenVINO DL Streamer - Edge AI Extension docker image.
* Update the 'lvaExtension' -> 'ENV' property to configure container behavior. Our example selects and `object_detection` pipeline and selects GPU inference

You will also need to create a graph topology with gRPC extension and then create a graph instance based on that topology. Here is a sample [operations.json](/samples/lva_ai_extension/topologies/operations.json).

# Additional Standalone Edge AI Extension Examples

### Selecting and Configuring Pipelines

Run with object classification pipeline specified on command line

```bash
$ ./docker/run_server.sh -–pipeline-name object_classification –pipeline-version vehicle_attributes_recognition
```

Run with classification pipeline with iGPU inference specified via environment variables
```
$ export PIPELINE_NAME=object_classification
$ export PIPELINE_VERSION=vehicle_attributes_recognition
$ export PARAMETERS={\"device\":\"GPU\"}
$ ./docker/run_server.sh
```

Notes:
* Only one pipeline can be enabled per container instance.
* If selecting a pipeline both name and version must be specified
* The `--debug` option selects debug pipelines that watermark inference results and saves images in `/tmp/vaserving/{--pipeline-version}/{timestamp}/` and can also be set using the environment variable DEBUG_PIPELINE
* The `--parameters` option specifies pipeline parameters for the selected pipeline. It can be either a JSON string or the name of a file containing the JSON. See the parameters section of the [pipeline definition](/docs/defining_pipelines.md#pipeline-parameters) document for more details. The individual definition files for [object_detection](/samples/lva_ai_extension/pipelines/object_detection/person_vehicle_bike_detection/pipeline.json), [object_classification](/samples/lva_ai_extension/pipelines/object_classification/vehicle_attributes_recognition/pipeline.json), and [object_tracking](/samples/lva_ai_extension/pipelines/object_tracking/person_vehicle_bike_tracking/pipeline.json) contain the supported parameters for the pre-loaded pipelines.
* To enable GPU inference use `--parameters "{\"device\":\"GPU\"}"

### Debug Mode

Debug pipelines can be selected using the `--debug` command line parameter or setting the `DEBUG_PIPELINE` environment variable. Debug pipelines save watermarked frames to `/tmp/vaserving/{--pipeline-version}/{timestamp}/` as JPEG images.

Run default pipeline in debug mode
```bash
$ ./docker/run_server.sh --debug
```

### Inference Using Intel iGPU

Pipelines can be configured to perform inference using Intel®
Integrated Graphics.

Run default pipeline with iGPU inference (be careful with escaping the JSON string)

```bash
$ ./docker/run_server.sh --parameters "{\"device\":\"GPU\"}"
```

### Logging
Run the following command to monitor the logs from the docker container
```bash
$ docker logs video-analytics-serving_0.4.0-dlstreamer-edge-ai-extension -f
```

### Developer Mode
The run script includes a `--dev` flag which starts the
container in "developer" mode. "Developer" mode sets `docker run`
options to make development and modification of media analytics
pipelines easier by allowing editing of source files on your host.

Here is an example of starting the AI Extension module in developer mode
```
$ ./docker/run_server.sh --dev
vaserving@host:~$ python3 samples/lva_ai_extension/server
<snip>
Starting Protocol Server Application on port 5001
```
The python application supports the same [options](#edge-ai-extension-module-options) as the `run_server.sh` script.

# Test Client
A test client is provided to demonstrate the capabilities of the Edge AI Extension module.
The test client script `run_client.sh` sends frames(s) to the extension module and prints inference results.
Use the --help option to see how to use the script. All arguments are optional.

```
$ ./docker/run_client.sh --help
usage: ./run_client.sh
  [ --server-ip : Specify the server ip to connect to ] (defaults to 127.0.0.1)
  [ --server-port : Specify the server port to connect to ] (defaults to 5001)
  [ --shared-memory : Enables and uses shared memory between client and server ] (defaults to off)
  [ --sample-file-path : Specify the sample file path to run] (defaults to samples/lva_ai_extension/sampleframes/sample01.png)
  [ --output-file-path : Specify the output file path to save inference results in jsonl format (defaults to /tmp/results.jsonl) ]
```
Notes
* Media or log file must be inside container or in /tmp which is a volume mounted path
* Either png or mp4 media files are supported
* If not using shared memory, decoded image frames must be less than 4MB (the maximum gPRC message size)
* If you are behind a firewall ensure `no_proxy` contains `127.0.0.1` in docker config and system settings.

Example of video inference using shared memory
```
$ wget -P /tmp https://github.com/intel-iot-devkit/sample-videos/blob/master/classroom.mp4
$ ./docker/run_client.sh --shared-memory --sample-file-path /tmp/classroom.mp4
```

# Building an Edge AI Extension Module Image
To build your own image follow the instructions below.

### Prerequisites
Building the image requires a modern Linux distro with the following packages installed:

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Video Analytics Serving requires Docker for it's build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Video Analytics Serving's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](/docs/installing_bash_macos.md). |

## Building the Image:

Run the docker image build script.
```
$ ./docker/build.sh
```
Resulting image name is `video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension`

# Updating or Changing Detection and Classification Models
Before updating the models used by a pipeline please see the format of
[pipeline definition files](/docs/defining_pipelines.md) and read the
tutorial on [changing object detection models](/docs/changing_object_detection_models.md).

Most of the steps to changes models are the same, but the existing
tutorial assumes you are working with the REST service and not the AI
Extension module. Use the developer mode to download new models and
add them to an existing pipeline as described. Note that the AI
Extension has different pipeline and model versions from the tutorial.
This table should help you adapt the steps in the tutorial to work for
the AI Extension.

|            | Pipeline Name    | Pipeline Version | Model Name  | Model Version |
|------------| -------------    | ------------- | ------------- | ------------- |
|Tutorial    | object_detection | 1             | object_detection | 1 |
|AI Extension| object_detection | person_vehicle_bike_detection  | person_vehicle_bike_detection | 1 |

Once you've made your changes, use the [test client](#test-client) to
start the pipeline and view results. Note: the original tutorial uses
a curl command that is not compatible with the AI Extension module.

