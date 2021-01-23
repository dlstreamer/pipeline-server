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

The OpenVINO™ DL Streamer - Edge AI Extension module can run as a standalone microservice or as a module within an Live Video Analytics graph. For more information on deploying the module as part of a Live Video Analytics graph please see [Configuring the AI Extension Module for Live Video Analytics](#configuring-the-ai-extension-module-for-live-video-analytics) and refer to the [Live Video Analytics documentation](https://azure.microsoft.com/en-us/services/media-services/live-video-analytics/). The following instructions demonstrate building and running the microservice and test client outside of Live Video Analytics.

## Building the Edge AI Extension Module Image

### Prerequisites
Building the image requires a modern Linux distro with the following packages installed:

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Video Analytics Serving requires Docker for it's build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Video Analytics Serving's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](/docs/installing_bash_macos.md). |

### Building the Image:

Run the docker image build script.
```
$ ./docker/build.sh
```
Resulting image name is `video-analytics-serving:0.4.1-dlstreamer-edge-ai-extension`

## Running the Edge AI Extension Module

To run the module as a standalone microservice with an `object_detection` pipeline use the `run_server.sh` script with default options. For examples of additional options see [Additional Standalone Edge AI Extension Examples](#additional-standalone-edge-ai-extension-examples).

```bash
$ ./docker/run_server.sh
<snip>
{"levelname": "INFO", "asctime": "2021-01-22 15:27:00,009", "message": "Starting DL Streamer Edge AI Extension on port: 5001", "module": "__main__"}
```

## Sending a Test Frame for Object Detection

To send a test frame to the microservice and receive `object_detection` results use the `run_client.sh` script.

```bash
$ ./docker/run_client.sh
[AIXC] [2021-01-22 15:28:06,956] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: Options for __main__.py
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: grpc_server_address == localhost:5001
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: grpc_server_ip == localhost
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: grpc_server_port == 5001
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: sample_file == /home/video-analytics-serving/samples/lva_ai_extension/sampleframes/sample01.png
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: loop_count == 0
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: fps_interval == 2
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: frame_rate == -1
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: frame_queue_size == 200
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,958] [MainThread  ] [INFO]: use_shared_memory == False
[AIXC] [2021-01-22 15:28:06,958] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:06,958] [MainThread  ] [INFO]: output_file == /tmp/result.jsonl
[AIXC] [2021-01-22 15:28:06,958] [MainThread  ] [INFO]: =======================
[AIXC] [2021-01-22 15:28:07,341] [Thread-2    ] [INFO]: MediaStreamDescriptor request #1
[AIXC] [2021-01-22 15:28:07,364] [Thread-2    ] [INFO]: MediaSample request #2
[AIXC] [2021-01-22 15:28:07,365] [MainThread  ] [INFO]: [Received] AckNum: 1
[AIXC] [2021-01-22 15:28:07,371] [Thread-2    ] [INFO]: MediaSample request #3
[AIXC] [2021-01-22 15:28:07,940] [Thread-3    ] [INFO]: [Received] AckNum: 2
[AIXC] [2021-01-22 15:28:07,940] [MainThread  ] [INFO]: Inference result 2
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (1.00) [0.30, 0.47, 0.09, 0.39] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.97) [0.36, 0.40, 0.05, 0.24] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.94) [0.44, 0.42, 0.08, 0.43] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.92) [0.57, 0.38, 0.05, 0.25] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.91) [0.69, 0.56, 0.12, 0.43] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.90) [0.68, 0.42, 0.04, 0.24] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.82) [0.64, 0.36, 0.05, 0.27] []
[AIXC] [2021-01-22 15:28:07,941] [MainThread  ] [INFO]: - person (0.60) [0.84, 0.44, 0.05, 0.29] []
[AIXC] [2021-01-22 15:28:07,943] [MainThread  ] [INFO]: Start Time: 1611347287.3661082 End Time: 1611347287.9434469 Frames Recieved: 1 FPS: 1.7320855292554225
[AIXC] [2021-01-22 15:28:07,943] [MainThread  ] [INFO]: Client finished execution
```

# Edge AI Extension Module Options

The module can be configured using command line options or environment variables (command line options take precedence).

| Setting             | Command line option   | Environment variable | Default value    |
|---------------------|-----------------------|----------------------|------------------|
| gRPC port           | -p                    | PORT                 | 5001             |
| Pipeline name       | --pipeline-name       | PIPELINE_NAME        | object_detection |
| Pipeline version    | --pipeline-version    | PIPELINE_VERSION     | person_vehicle_bike_detection |
| Pipeline parameters | --pipeline-parameters | PIPELINE_PARAMETERS  | {}                |
| Use debug pipeline  | --debug               | DEBUG_PIPELINE       |                   |

## Video Analytics Pipelines

The following pipelines are included in the AI Extension:

| Name          | Version       | Definition      | Diagram |
| ------------- | ------------- | --------------- | ------- |
| object_detection | person_vehicle_bike_detection  | [definition](/samples/lva_ai_extension/pipelines/object_detection/person_vehicle_bike_detection/pipeline.json)|![diagram](pipeline_diagrams/object-detection.png)|
| object_classification  | vehicle_attributes_recognition  | [definition](/samples/lva_ai_extension/pipelines/object_classification/vehicle_attributes_recognition/pipeline.json)|![diagram](pipeline_diagrams/object-classification.png)|
| object_tracking  | person_vehicle_bike_tracking  | [definition](/samples/lva_ai_extension/pipelines/object_tracking/person_vehicle_bike_tracking/pipeline.json)|![diagram](pipeline_diagrams/object-tracking.png)|


## Configuring the AI Extension Module for Live Video Analytics

Based on HW target, choose and update the appropriate deployment manifest located in the [deployment directory](/samples/lva_ai_extension/deployment/).
* Make sure that the 'lvaExtension'->'image' property shows the Azure URI of VAS LVA Edge AI Extension docker image.
* Update the 'lvaExtension' -> 'ENV' property to configure container behavior. Our manifest file is configured for object detection by default.

You will also need to create a graph topology with gRPC extension and then create a graph instance based on that topology. Here is a sample [operations.json](/samples/lva_ai_extension/topologies/operations.json).

# Additional Standalone Edge AI Extension Examples

### Specifying VAServing parameters for LVA Server

The LVA Server application will filter command line arguments between the LVA layer and VAServing layer.
Command line arguments are first handled by run_server.sh; if not specifically handled by run_server.sh the argument
is passed into the LVA Server application.
Command line arguments that are not recognized by LVA Server are then passed to VAServing, if VAServing does not recognize
the arguments an error will be reported

```bash
./docker/run_server.sh --log_level DEBUG
```

### Selecting and Configuring Pipelines

Run with object classification pipeline specified on command line

```bash
$ ./docker/run_server.sh -–pipeline-name object_classification –pipeline-version vehicle_attributes_recognition
```

Run with classification pipeline with iGPU inference specified via environment variables
```
$ export PIPELINE_NAME=object_classification
$ export PIPELINE_VERSION=vehicle_attributes_recognition
$ export PIPELINE_PARAMETERS='{"detection-device":"GPU","classification-device":"GPU"}'
$ ./docker/run_server.sh
```

Notes:
* Parameter `device` has changed to `detection-device` for detection model and `classification-device` for classification model, refer to example above on how to set.
* Only one pipeline can be enabled per container instance.
* If selecting a pipeline both name and version must be specified
* The `--debug` option selects debug pipelines that watermark inference results and saves images in `/tmp/vaserving/{--pipeline-version}/{timestamp}/` and can also be set using the environment variable DEBUG_PIPELINE
* The `--parameters` option specifies pipeline parameters for the selected pipeline. It can be either a JSON string or the name of a file containing the JSON. See the parameters section of the [pipeline definition](/docs/defining_pipelines.md#pipeline-parameters) document for more details. The individual definition files for [object_detection](/samples/lva_ai_extension/pipelines/object_detection/person_vehicle_bike_detection/pipeline.json), [object_classification](/samples/lva_ai_extension/pipelines/object_classification/vehicle_attributes_recognition/pipeline.json), and [object_tracking](/samples/lva_ai_extension/pipelines/object_tracking/person_vehicle_bike_tracking/pipeline.json) contain the supported parameters for the pre-loaded pipelines.

### Debug Mode

Debug pipelines can be selected using the `--debug` command line parameter or setting the `DEBUG_PIPELINE` environment variable. Debug pipelines save watermarked frames to `/tmp/vaserving/{--pipeline-version}/{timestamp}/` as JPEG images.

Run default pipeline in debug mode
```bash
$ ./docker/run_server.sh --debug
```

### Inference Accelerators

Pipelines can be configured to perform inference using a range of accelerators.
This is a two step process:
1. Give docker access to the accelerator's resources
2. Set the inference accelerator device name when starting the pipeline

See [Enabling Hardware Accelerators](/docs/running_video_analytics_serving.md#enabling-hardware-accelerators)
for details on docker resources and inference device name for supported accelerators.
This will allow you to customize the deployment manifest for a given accelerator.

The run server script will automatically detect installed accelerators and provide access to their resources.
Here we run the default pipeline with inference running on Intel® Integrated Graphics (be careful with escaping the JSON string)
```bash
$ ./docker/run_server.sh --pipeline-parameters '{"detection-device":"GPU"}'
```

### Logging
Run the following command to monitor the logs from the docker container
```bash
$ docker logs video-analytics-serving_0.4.1-dlstreamer-edge-ai-extension -f
```

### Developer Mode
The server run script includes a `--dev` flag which starts the container in "developer" mode.
This mode runs with files from the host, not the container, which is useful for quick iteration and development.
```bash
$ ./docker/run_server.sh --dev
```

# Test Client
A test client is provided to demonstrate the capabilities of the Edge AI Extension module.
The test client script `run_client.sh` sends frames(s) to the extension module and prints inference results.
Use the --help option to see how to use the script. All arguments are optional.

```
$ ./docker/run_client.sh
All arguments are optional, usage is as follows
  [ --server-ip : Specify the server ip to connect to ] (defaults to 127.0.0.1)
  [ --server-port : Specify the server port to connect to ] (defaults to 5001)
  [ --shared-memory : Enables and uses shared memory between client and server ] (defaults to off)
  [ --sample-file-path : Specify the sample file path to run] (defaults to samples/lva_ai_extension/sampleframes/sample01.png)
  [ --output-file-path : Specify the output file path to save inference results in jsonl format] (defaults to /tmp/results.jsonl)
  [ --number-of-streams : Specify number of streams (one client process per stream)]
  [--fps-interval FPS_INTERVAL] (interval between frames in seconds, defaults to 0)
  [--frame-rate FRAME_RATE] (send frames at given fps, default is no limit)
  [ --dev : Mount local source code] (use for development)
  ```
Notes:
* Media or log file must be inside container or in volume mounted path
* Either png or mp4 media files are supported
* If not using shared memory, decoded image frames must be less than 4MB (the maximum gPRC message size)
* If you are behind a firewall ensure `no_proxy` contains `127.0.0.1` in docker config and system settings.

# Updating or Changing Detection and Classification Models
Before updating the models used by a pipeline please see the format of
[pipeline definition files](/docs/defining_pipelines.md) and read the
tutorial on [changing object detection models](/docs/changing_object_detection_models.md).

Most of the steps to changes models used by LVA extension are the same as for the above tutorial, but it assumes you are working with the REST service and not the AI
Extension module. The LVA specific steps are called out in the following sections.

## Run Existing Object Detection Pipeline
Get baseline results for existing object_detection model `person-vehicle-bike-detection-crossroad-0078`

```
$./docker/run_server.sh
<snip>
/object_classification/vehicle_attributes_recognition/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 12:10:10,288", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 12:10:10,288", "message": "Completed Loading Pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 12:10:10,289", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 12:10:10,292", "message": "Starting DL Streamer Edge AI Extension on port: 5001", "module": "__main__"}
```

In a separate terminal:

```
$ ./docker/run_client.sh
<snip>
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (1.00) [0.30, 0.47, 0.09, 0.39]
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (0.97) [0.36, 0.40, 0.05, 0.24]
[AIXC] [2020-11-20 23:29:11,417] [MainThread  ] [INFO]: - person (0.94) [0.44, 0.42, 0.08, 0.43]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.92) [0.57, 0.38, 0.05, 0.25]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.91) [0.69, 0.56, 0.12, 0.43]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.90) [0.68, 0.42, 0.04, 0.24]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.82) [0.64, 0.36, 0.05, 0.27]
[AIXC] [2020-11-20 23:29:11,418] [MainThread  ] [INFO]: - person (0.60) [0.84, 0.44, 0.05, 0.29]
<snip>
```
## Add New Model to Models List

Copy the existing model list `models/models.list.yml` to `models/yolo-models.list.yml` then add the following entry:

```yml
- model: yolo-v2-tiny-tf
  alias: yolo
  version: 1
  precision: [FP16,FP32]
```

## Update Pipeline Definition File to Use New Model

Copy, rename and update the existing object detection pipeline to reference `yolo-v2-tiny-tf` model:

```bash
$ cp -r pipelines/object_detection/person_vehicle_bike_detection pipelines/object_detection/yolo
$ sed -i -e s/person_vehicle_bike_detection/yolo/g pipelines/object_detection/yolo/pipeline.json
```

## Rebuild Edge AI Extension with new Model and Pipeline

```
$ ./docker/build.sh --models models/yolo-models.list.yml
```

The model will now be in `models` folder in the root of the project:

```
models
└── yolo
    └── 1
        ├── FP16
        │   ├── yolo-v2-tiny-tf.bin
        │   ├── yolo-v2-tiny-tf.mapping
        │   └── yolo-v2-tiny-tf.xml
        ├── FP32
        │   ├── yolo-v2-tiny-tf.bin
        │   ├── yolo-v2-tiny-tf.mapping
        │   └── yolo-v2-tiny-tf.xml
        └── yolo-v2-tiny-tf.json
```

Check that expected model and pipeline are present in the built image:

```bash
$ docker run -it --entrypoint /bin/bash video-analytics-serving:0.4.1-dlstreamer-edge-ai-extension
vaserving@82dd59743ca3:~$ ls models
person_vehicle_bike_detection  vehicle_attributes_recognition  yolo
vaserving@82dd59743ca3:~$  ls pipelines/object_detection/
debug_person_vehicle_bike_detection  person_vehicle_bike_detection  yolo
```

## Run Edge AI Extension with new Model and Pipeline

### Re-start service
Restart the service to ensure we are using the image with the yolo-v2-tiny-tf model
```
$ docker stop video-analytics-serving:0.4.1-dlstreamer-edge-ai-extension
$ docker/run_server.sh --pipeline-name object_detection --pipeline-version yolo
```
### Run the client
Note different results due to different model
```
$ docker/run_client.sh
<snip>
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.82) [0.63, 0.36, 0.06, 0.24] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.78) [0.56, 0.37, 0.06, 0.23] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.63) [0.44, 0.43, 0.11, 0.43] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.63) [0.31, 0.45, 0.09, 0.23] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.62) [0.69, 0.38, 0.06, 0.23] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.60) [0.40, 0.44, 0.07, 0.27] []
[AIXC] [2021-01-07 06:51:13,081] [MainThread  ] [INFO]: - person (0.59) [0.45, 0.43, 0.08, 0.29] []
[AIXC] [2021-01-07 06:51:13,082] [MainThread  ] [INFO]: - person (0.57) [0.33, 0.40, 0.07, 0.20] []
[AIXC] [2021-01-07 06:51:13,082] [MainThread  ] [INFO]: - person (0.57) [0.76, 0.46, 0.13, 0.23] []
[AIXC] [2021-01-07 06:51:13,082] [MainThread  ] [INFO]: - person (0.55) [0.41, 0.44, 0.03, 0.10] []
<snip>
```
