# OpenVINO™ DL Streamer – Edge AI Extension Module

| [Getting Started](#getting-started) | [Edge AI Extension Module Options](#edge-ai-extension-module-options) | [Additional Examples](#additional-standalone-edge-ai-extension-examples) | [Spatial Analytics](#spatial-analytics-pipelines)| [Test Client](#test-client) |
[Changing Models](#updating-or-changing-detection-and-classification-models)

The OpenVINO™ DL Streamer - Edge AI Extension module is a microservice based on [Video Analytics Serving](/README.md) that provides video analytics pipelines built with OpenVINO™ DL Streamer. Developers can send decoded video frames to the AI Extension module which performs detection, classification, or tracking and returns the results. The AI Extension module exposes [gRPC APIs](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/grpc-extension-protocol) that are compatible with [Azure Video Analyzer](https://azure.microsoft.com/en-us/products/video-analyzer/) (AVA). Powered by OpenVINO™ toolkit, the AI Extension module enables developers to build, optimize and deploy deep learning inference workloads for maximum performance across Intel® architectures.

## Highlights

- Spatial analytics features: [Object Line Crossing](#object-line-crossing) and [Object Zone Count](#object-zone-count) similar to [Azure Video Analyzer Spatial Analysis](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/computer-vision-for-spatial-analysis?tabs=azure-stack-edge) 
- Scalable, high-performance solution for serving video analytics pipelines on Intel® architectures
- gRPC API enabling fast data transfer rate and low latency
- Supported Configuration: Pre-built Ubuntu Linux container for CPU and iGPU
- Pre-loaded Object Detection, Object Classification, Object Tracking and Action Recognition pipelines to get started quickly
- Pre-loaded models - see table below.

| Name | Version   | Model |
| -----|-----------| ------|
| person_vehicle_bike_detection| 1 |[person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/person-vehicle-bike-detection-crossroad-0078/README.md)|
| object_detection|person|[person-detection-retail-0013](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/person-detection-retail-0013/README.md)|
| object_detection|vehicle|[vehicle-detection-0202](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/vehicle-detection-0202/README.md)|
| vehicle_attributes_recognition|1|[vehicle-attributes-recognition-barrier-0039](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/vehicle-attributes-recognition-barrier-0039/README.md)|
| action_recognition|decoder|[action-recognition-0001-decoder](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/action-recognition-0001/README.md)|
| action_recognition|encoder|[action-recognition-0001-encoder](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/action-recognition-0001/README.md)|


## What's New

- Action Recognition pipeline (preview feature). 
- Deployment manifest, topology and operations file are now provided by the [Intel OpenVINO™ DL Streamer – Edge AI Extension Tutorial](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/use-intel-grpc-video-analytics-serving-tutorial).


# Getting Started

The OpenVINO™ DL Streamer - Edge AI Extension module can run as a standalone microservice or as a module within an Azure Video Analyzer graph. For more information on deploying the module as part of a Azure Video Analyzer graph please see [Configuring the AI Extension Module for Azure Video Analyzer](#configuring-the-ai-extension-module-for-live-video-analytics) and refer to the [Azure Video Analyzer documentation](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/overview). The following instructions demonstrate building and running the microservice and test client outside of Azure Video Analyzer.

## Building the Edge AI Extension Module Image

### Prerequisites
Building the image requires a modern Linux distro with the following packages installed:

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Video Analytics Serving requires Docker for it's build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Video Analytics Serving's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](/docs/installing_bash_macos.md). |

### Building the Image

Run the docker image build script.
```
$ ./docker/build.sh
```
Resulting image name is `video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension`

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
[AIXC] [2021-01-22 15:28:06,957] [MainThread  ] [INFO]: sample_file == /home/video-analytics-serving/samples/ava_ai_extension/sampleframes/sample01.png
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
| RSTP Re-Streaming   | --enable-rtsp         | ENABLE_RTSP          | false            |
| Pipeline name       | --pipeline-name       | PIPELINE_NAME        | object_detection |
| Pipeline version    | --pipeline-version    | PIPELINE_VERSION     | person_vehicle_bike_detection |
| Use debug pipeline  | --debug               | DEBUG_PIPELINE       |                   |

## Video Analytics Pipelines

The following pipelines are included in the AI Extension:

| Name          | Version       | Definition      | Diagram |
| ------------- | ------------- | --------------- | ------- |
| object_detection | person_vehicle_bike_detection  | [definition](/samples/ava_ai_extension/pipelines/object_detection/person_vehicle_bike_detection/pipeline.json)|![diagram](pipeline_diagrams/object-detection.png)|
| object_detection | object_zone_count | [definition](/samples/ava_ai_extension/pipelines/object_detection/object_zone_count/pipeline.json)|![diagram](pipeline_diagrams/zone-detection.png)|
| object_classification  | vehicle_attributes_recognition  | [definition](/samples/ava_ai_extension/pipelines/object_classification/vehicle_attributes_recognition/pipeline.json)|![diagram](pipeline_diagrams/object-classification.png)|
| object_tracking  | person_vehicle_bike_tracking  | [definition](/samples/ava_ai_extension/pipelines/object_tracking/person_vehicle_bike_tracking/pipeline.json)|![diagram](pipeline_diagrams/object-tracking.png)|
| object_tracking  | object_line_crossing  | [definition](/samples/ava_ai_extension/pipelines/object_tracking/object_line_crossing/pipeline.json)|![diagram](pipeline_diagrams/line-crossing.png)|
| action_recognition | general  | [definition](/samples/ava_ai_extension/pipelines/action_recognition/general/pipeline.json)|![diagram](pipeline_diagrams/action-recognition.png)|

There are three versions of the object zone count pipeline. They are all based on the same pipeline design but use different detection models.

| Pipeline Version | Model |
| ---------------- |-------|
| object_zone_count| [person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/person-vehicle-bike-detection-crossroad-0078/README.md)|
| object_zone_count_person| [person-detection-retail-0013](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/person-detection-retail-0013/README.md)|
| object_zone_count_vehicle| [vehicle-detection-0202](https://github.com/openvinotoolkit/open_model_zoo/blob/2021.4/models/intel/vehicle-detection-0202/README.md)|


## Extension Configuration

The Azure Video Analyzer (AVA) Server supports the extension_configuration field in the [MediaStreamDescriptor message](https://raw.githubusercontent.com/Azure/video-analyzer/main/contracts/grpc/extension.proto#L69). This field contains a JSON string that must match the extension configuration schema. See example below. Note that pipeline name and version fields are required but parameters and frame-destination are optional.
```
{
    "pipeline": {
        "name": "object_detection",
        "version": "person_vehicle_bike_detection",
        "parameters": {},
        "frame-destination": {}
    }
}
```

## Inference Accelerators

Pipelines can be configured to perform inference using a range of accelerators.
This is a two step process:
1. Give docker access to the accelerator's resources
2. Set the inference accelerator device name when starting the pipeline

See [Enabling Hardware Accelerators](/docs/running_video_analytics_serving.md#enabling-hardware-accelerators)
for details on docker resources and inference device name for supported accelerators.
This will allow you to customize the deployment manifest for a given accelerator.

The run server script will automatically detect installed accelerators and provide access to their resources.

Pipelines will define a default accelerator in their .json files. To run a pipeline on a different accelerator modify the pipeline json or send in a gRPC request with a extension_configuration. The Azure Video Analyzer (AVA) client generates this gRPC request with the extension configuration

Example extension_configuration
```
{
    "pipeline": {
        "name": "object_detection",
        "version": "person_vehicle_bike_detection",
        "parameters": { "detection-device": "GPU"}
    }
}
```
## Configuring the AI Extension Module for Azure Video Analyzer

Please refer to the [Analyze live video with Intel OpenVINO™ DL Streamer – Edge AI Extension](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/use-intel-grpc-video-analytics-serving-tutorial) tutorial for deployment manifests, topologies or operations files and other details. 


# Additional Standalone Edge AI Extension Examples

### Specifying VA Serving parameters for AVA Server

The AVA Server application will filter command line arguments between the AVA layer and VA Serving layer.
Command line arguments are first handled by run_server.sh; if not specifically handled by run_server.sh the argument
is passed into the AVA Server application.
Command line arguments that are not recognized by AVA Server are then passed to VA Serving, if VA Serving does not recognize
the arguments an error will be reported.

```bash
./docker/run_server.sh --log_level DEBUG
```

### Real Time Streaming Protocol (RTSP) Re-streaming

Pipelines can be configured to connect and visualize input video with superimposed bounding boxes.

* Enable RTSP at Server start
```
$ ./docker/run_server.sh --enable-rtsp
```
* Run client with frame destination set. For demonstration, path set as `person-detection` in example request below.
```
$ ./docker/run_client.sh --pipeline-name object_detection --pipeline-version person_vehicle_bike_detection --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=true --frame-destination '{\"type\":\"rtsp\",\"path\":\"person-detection\"}'
```
* Connect and visualize: Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/person-detection`.

* Example extension_configuration for re streaming pipeline.
```
{
    "pipeline": {
        "name": "object_detection",
        "version": "person_vehicle_bike_detection",
        "frame-destination": { "type":"rtsp", "path":"person-detection"}
    }
}
```

### Logging
Run the following command to monitor the logs from the docker container
```bash
$ docker logs video-analytics-serving_0.6.1-dlstreamer-edge-ai-extension -f
```

### Developer Mode
The server run script includes a `--dev` flag which starts the container in "developer" mode.
This mode runs with files from the host, not the container, which is useful for quick iteration and development.
```bash
$ ./docker/run_server.sh --dev
```

### Selecting Pipelines
>**Note:** These features are deprecated and will be removed in a future release. Please use extension configuration instead.

Specify the default pipeline via command line and run the server

```bash
$ ./docker/run_server.sh --pipeline-name object_classification --pipeline-version vehicle_attributes_recognition
```

Specify the default pipeline via environment variables and run the server
```
$ export PIPELINE_NAME=object_classification
$ export PIPELINE_VERSION=vehicle_attributes_recognition
$ ./docker/run_server.sh
```

Notes:
* If selecting a pipeline both name and version must be specified
* The `--debug` option selects debug pipelines that watermark inference results and saves images in `/tmp/vaserving/{--pipeline-version}/{timestamp}/` and can also be set using the environment variable DEBUG_PIPELINE

### Debug Mode
>**Note:** This feature is deprecated and will be removed in a future release. Please use RTSP re-streaming instead.

Debug pipelines can be selected using the `--debug` command line parameter or setting the `DEBUG_PIPELINE` environment variable. Debug pipelines save watermarked frames to `/tmp/vaserving/{--pipeline-version}/{timestamp}/` as JPEG images.

Run default pipeline in debug mode
```bash
$ ./docker/run_server.sh --debug
```

# Spatial Analytics Pipelines
## Object Zone Count
The [object_detection/object_zone_count](./pipelines/object_detection/object_zone_count/pipeline.json) pipeline generates events containing objects detected in zones defined by the AVA extension configuration. For more information on the underlying zone event operation, see object_zone_count [README](../../extensions/spatial_analytics/object_zone_count.md).

### Build and Run

1. Build and run AVA server as normal

2. Run client with example extension configuration. The `object_zone_count.json` extension configuration contains zone definitions to generate `object-zone-count` events for a media stream. Look for the below events in client output:

   ```
   $ ./docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/ava_ai_extension/client/extension-config/object_zone_count.json
   ```
   ```
   <snip>
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (1.00) [0.30, 0.47, 0.09, 0.39] ['inferenceId: 4ea7a39d41eb4befae87894a48e1ea6a', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.97) [0.36, 0.40, 0.05, 0.24] ['inferenceId: 287b569a93fb4d4386af3cb0871b52ca', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.94) [0.44, 0.42, 0.08, 0.43] ['inferenceId: 4e82d111fccc4649a650fe205f70d079', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.92) [0.57, 0.38, 0.05, 0.25] ['inferenceId: cdc5e1dfa20a41b69bb05d3289e773d5', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.91) [0.69, 0.56, 0.12, 0.43] ['inferenceId: d873d43a9e274e5b8693b1df87764e30', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.90) [0.68, 0.42, 0.04, 0.24] ['inferenceId: ab759106752a45279007bae98eabd032', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.82) [0.64, 0.36, 0.05, 0.27] ['inferenceId: 908960e242334549a52bafb33f6a29a0', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,607] [MainThread  ] [INFO]: ENTITY - person (0.60) [0.84, 0.44, 0.05, 0.29] ['inferenceId: 1a74f84445cf49cbb517ff2ea83f74c3', 'subtype: objectDetection']
   [AIXC] [2021-09-09 19:50:45,608] [MainThread  ] [INFO]: EVENT - Zone2: ['inferenceId: fe65126e0db64e659b6414345d52a96c', 'subtype: object-zone-count', "relatedInferences: ['4ea7a39d41eb4befae87894a48e1ea6a']", "status: ['intersects']", 'zone-count: 1']
   [AIXC] [2021-09-09 19:50:45,608] [MainThread  ] [INFO]: EVENT - Zone3: ['inferenceId: 2b1685ebe9914805b962615e19116b87', 'subtype: object-zone-count', "relatedInferences: ['287b569a93fb4d4386af3cb0871b52ca', '4e82d111fccc4649a650fe205f70d079', 'cdc5e1dfa20a41b69bb05d3289e773d5', 'd873d43a9e274e5b8693b1df87764e30', 'ab759106752a45279007bae98eabd032', '908960e242334549a52bafb33f6a29a0', '1a74f84445cf49cbb517ff2ea83f74c3']", "status: ['intersects', 'intersects', 'within', 'intersects', 'within', 'within', 'intersects']", 'zone-count: 7']
   ```

### Enabling RTSP Output

To get a visual of `object_zone_count` extension, run with `object_zone_count_rendered.json` extension configuration which sets `enable_watermark` and `frame-destination` parameters for RTSP re streaming.

> gvawatermark does not draw the polygon lines but markers/dots showing the boundary of the defined polygon regions, so the viewer must currently "connect the dots" themself.

1. Build and run AVA server as normal but with `--enable-rtsp` flag

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/ava_ai_extension/client/extension-config/object_zone_count_rendered.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
   ```
3. Connect and visualize: Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/zone-events`.

## Object Line Crossing
The [object_tracking/object_line_crossing](./pipelines/object_tracking/object_line_crossing/pipeline.json) pipeline generates events containing objects which crossed lines defined by the AVA extension configuration. For more information on the underlying line crossing operation, see object_line_crossing [README](../../extensions/spatial_analytics/object_line_crossing.md).

### Build and Run

1. Build and run AVA server as normal

2. Run client with example extension configuration. The `line_cross_tracking_config.json` extension configuration contains example line definitions needed to generate`object_line_crossing` events for a media stream. Look for the below events in client output:

   ```
   $ ./docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/ava_ai_extension/client/extension-config/object_line_crossing.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=True
   ```
   ```
   <snip>
   [AIXC] [2021-05-12 18:57:01,315] [MainThread  ] [INFO]: ENTITY - person (1.00) [0.40, 0.27, 0.12, 0.62] ['inferenceId: d47a4192ca4b4933a6c6c588220f59de', 'subtype: objectDetection', 'id: 1']
   [AIXC] [2021-05-12 18:57:01,315] [MainThread  ] [INFO]: EVENT - hallway_bottom: ['inferenceId: 520d7506e5c94f3b9aeb1d157af6311c', 'subtype: lineCrossing', "relatedInferences: ['d47a4192ca4b4933a6c6c588220f59de']", 'counterclockwiseTotal: 1', 'total: 1', 'clockwiseTotal: 0', 'direction: counterclockwise']
   ```

### Enabling RTSP Output

Adding a configuration parameter to specify the frame-destination enables a secondary workflow, with VA Serving rendering visualization of lines and entity detections/events (shown below).

By setting `enable_watermark` and `frame-destination` parameter for RTSP re streaming, the caller may visualize the output. This added to the `line_cross_tracking_config_rtsp.json` extension configuration. So following the same instructions above but swapping the extension configuration used will dynamically produce the scene using rudimentary markers/dots showing the start and end points of defined lines. This allows the DL Streamer `gvawatermark` element (used in the frame-destination) to handle rendering.



To get a visual of `object_line_crossing` extension, run with `object_line_crossing_rendered.json` extension configuration which sets `enable_watermark` and `frame-destination` parameters for RTSP re streaming.

> gvawatermark does not draw the lines, so the viewer must currently "connect the dots" themself.

1. Build and run AVA server as normal but with `--enable-rtsp` flag

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/ava_ai_extension/client/extension-config/object_line_crossing_rendered.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=True
   ```

3. Connect and visualize: Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/vaserving`.

# Test Client
A test client is provided to demonstrate the capabilities of the Edge AI Extension module.
The test client script `run_client.sh` sends frames(s) to the extension module and prints inference results.
Use the --help option to see how to use the script. All arguments are optional.

```
$ ./docker/run_client.sh
All arguments are optional, usage is as follows
  [ -s : gRPC server address, defaults to None]
  [ --server-ip : Specify the server ip to connect to ] (defaults to 127.0.0.1)
  [ --server-port : Specify the server port to connect to ] (defaults to 5001)
  [ --sample-file-path : Specify the sample file path to run] (defaults to samples/ava_ai_extension/sampleframes/sample01.png)
  [ --loop-count : How many times to loop the source after it finishes ]
  [ --number-of-streams : Specify number of streams (one client process per stream)]
  [ --fps-interval FPS_INTERVAL] (interval between frames in seconds, defaults to 0)
  [ --frame-rate FRAME_RATE] (send frames at given fps, default is no limit)
  [ --frame-queue-size : Max number of frames to buffer in client, defaults to 200]
  [ --shared-memory : Enables and uses shared memory between client and server ] (defaults to off)
  [ --output-file-path : Specify the output file path to save inference results in jsonl format] (defaults to /tmp/results.jsonl)
  [ --extension-config : JSON string or file containing extension configuration]
  [ --pipeline-name : Name of the pipeline to run]
  [ --pipeline-version : Name of the pipeline version to run]
  [ --pipeline-parameters : Pipeline parameters]
  [ --pipeline-extensions : JSON string containing tags to be added to extensions field in results]
  [ --frame-destination : Frame destination for rtsp restreaming]
  [ --dev : Mount local source code] (use for development)
  ```
Notes:
* If using `--extension-config`, you must not set any of the following options
  * --pipeline-name
  * --pipeline-version
  * --pipeline-parameters
  * --pipeline-extensions
  * --frame-destination
* Media or log file must be inside container or in volume mounted path
* Either png or mp4 media files are supported
* If not using shared memory, decoded image frames must be less than 4MB (the maximum gPRC message size)
* If you are behind a firewall ensure `no_proxy` contains `127.0.0.1` in docker config and system settings.

# Updating or Changing Detection and Classification Models
Before updating the models used by a pipeline please see the format of
[pipeline definition files](/docs/defining_pipelines.md) and read the
tutorial on [changing object detection models](/docs/changing_object_detection_models.md).

Most of the steps to changes models used by AVA extension are the same as for the above tutorial, but it assumes you are working with the REST service and not the AI
Extension module. The AVA specific steps are called out in the following sections.

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

## Send a request to the server to run a different pipeline
```
$ ./docker/run_client.sh --pipeline-name object_classification --pipeline-version vehicle_attributes_recognition
```

## Send a request to the server to run a different pipeline on the GPU
```
$ ./docker/run_client.sh --pipeline-name object_detection --pipeline-version person_vehicle_bike_detection --pipeline-parameters '{\"detection-device\":\"GPU\"}'
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
$ docker run -it --entrypoint /bin/bash video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension
vaserving@82dd59743ca3:~$ ls models
person_vehicle_bike_detection  vehicle_attributes_recognition  yolo
vaserving@82dd59743ca3:~$  ls pipelines/object_detection/
debug_person_vehicle_bike_detection  person_vehicle_bike_detection  yolo
```

## Run Edge AI Extension with new Model and Pipeline

### Restart service
Restart the service to ensure we are using the image with the yolo-v2-tiny-tf model
```
$ docker stop video-analytics-serving_0.6.1-dlstreamer-edge-ai-extension
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
