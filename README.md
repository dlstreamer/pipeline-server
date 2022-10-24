# Intel® Deep Learning Streamer Pipeline Server

| [Getting Started](#getting-started)
| [Request Customizations](#request-customizations)
| [Changing Pipeline Model](#changing-pipeline-model)
| [Further Reading](#further-reading)
| [Known Issues](#known-issues) |

Intel® Deep Learning Streamer (Intel® DL Streamer) Pipeline Server is a python package and microservice for
deploying optimized media analytics pipelines. It supports pipelines
defined in
[GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)*
or [FFmpeg](https://ffmpeg.org/)* and provides APIs to discover, start,
stop, customize and monitor pipeline execution. Intel® DL Streamer Pipeline Server is based on [Intel® Deep Learning Streamer Pipeline Framework](https://github.com/dlstreamer/dlstreamer) and [FFmpeg Video Analytics](https://github.com/VCDP/FFmpeg-patch).

## Features Include

| |                  |
|---------------------------------------------|------------------|
| **Customizable Media Analytics Containers** | Scripts and dockerfiles to build and run container images with the required dependencies for hardware optimized media analytics pipelines. |
| **No-Code Pipeline Definitions and Templates** | JSON based definition files, a flexible way for developers to define and parameterize pipelines while abstracting the low level details from their users. |
| **Deep Learning Model Integration** | A simple way to package and reference [OpenVINO<sup>&#8482;</sup>](https://software.intel.com/en-us/openvino-toolkit) based models in pipeline definitions. The precision of a model can be auto-selected at runtime based on the chosen inference device. |
| **Intel® DL Streamer Pipeline Server Python API** | A python module to discover, start, stop, customize and monitor pipelines based on their no-code definitions. |
| **Intel® DL Streamer Pipeline Server Microservice** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| A RESTful microservice providing endpoints and APIs matching the functionality of the python module. |

> **IMPORTANT:** Intel® DL Streamer Pipeline Server is provided as a _sample_. It
> is not intended to be deployed into production environments without
> modification. Developers deploying Intel® DL Streamer Pipeline Server should
> review it against their production requirements.

The sample microservice includes five categories of media analytics pipelines. Click on the links below to find out more about each of them.

| |                  |
|---------------------------------------------|---------|
| **[object_detection](pipelines/gstreamer/object_detection)** | Detect and label objects
| **[object_classification](pipelines/gstreamer/object_classification)** | As object_detection adding meta-data such as object subtype and color
| **[object_tracking](pipelines/gstreamer/object_tracking)** | As object_classification adding tracking identifier to meta-data
| **[audio_detection](pipelines/gstreamer/audio_detection)** | Analyze audio streams for events such as breaking glass or barking dogs.

# Getting Started

## Prerequisites

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Intel® DL Streamer Pipeline Server requires Docker for its build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Intel® DL Streamer Pipeline Server's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](docs/installing_bash_macos.md). |

## Supported Hardware

Refer to [Intel® DL Streamer Hardware Requirements](https://dlstreamer.github.io/get_started/hardware_requirements.html) for supported development and target runtime platforms and the [Intel® DL Streamer Install Guide](https://dlstreamer.github.io/get_started/install/install_guide_ubuntu.html) for details on providing access to accelerator devices.

## Building the Microservice

Build the sample microservice with the following command:

```bash
./docker/build.sh
```

The script will automatically include the sample models, pipelines and
required dependencies.

To verify the build succeeded execute the following command:

```bash
docker images dlstreamer-pipeline-server-gstreamer:latest
```

Expected output:

```bash
REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
dlstreamer-pipeline-server-gstreamer   latest              f51f2695639f        2 minutes ago          2.81GB
```

## Running the Microservice

Start the sample microservice with the following command:

```bash
./docker/run.sh -v /tmp:/tmp
```

This script issues a standard docker run command to launch the
container, run a Tornado based web service on port 8080, and mount the
`/tmp` folder. The `/tmp` folder is mounted to share sample
results with the host and is optional in actual deployments.

Expected output:

```text
{"levelname": "INFO", "asctime": "2021-04-05 23:43:42,406", "message": "=================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:42,406", "message": "Loading Pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:42,406", "message": "=================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,073", "message": "Loading Pipelines from Config Path /home/pipeline-server/pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,088", "message": "Loading Pipeline: audio_detection version: environment type: GStreamer from /home/pipeline-server/pipelines/audio_detection/environment/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,090", "message": "Loading Pipeline: object_classification version: vehicle_attributes type: GStreamer from /home/pipeline-server/pipelines/object_classification/vehicle_attributes/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,102", "message": "Loading Pipeline: object_detection version: edgex type: GStreamer from /home/pipeline-server/pipelines/object_detection/edgex/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,104", "message": "Loading Pipeline: object_detection version: person_vehicle_bike type: GStreamer from /home/pipeline-server/pipelines/object_detection/person_vehicle_bike/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,109", "message": "Loading Pipeline: object_tracking version: person_vehicle_bike type: GStreamer from /home/pipeline-server/pipelines/object_tracking/person_vehicle_bike/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,109", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,109", "message": "Completed Loading Pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,109", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-05 23:43:43,217", "message": "Starting Tornado Server on port: 8080", "module": "__main__"}
```

## Running a Pipeline

The Pipeline Server includes a sample client [pipeline_client](./client/README.md) that can connect to the service and make requests. We will use pipeline_client to explain how to use the key microservice features.
> **Note:** Any RESTful tool or library can be used to send requests to the Pipeline Server service. We are using pipeline_client as it simplifies interaction with the service.

> **Note:**  The microservice has to be up and running before the sample client is invoked.

Before running a pipeline, we need to know what pipelines are available. We do this using pipeline_client's `list-pipeline` command.
In new shell run the following command:

```bash
./client/pipeline_client.sh list-pipelines
 ```

 ```text
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - object_tracking/object_line_crossing
 - object_tracking/person_vehicle_bike
 - object_detection/object_zone_count
 - object_detection/app_src_dst
 - object_detection/person_vehicle_bike
```

> **Note:** The pipelines you will see may differ slightly

Pipelines are displayed as a name/version tuple. The name reflects the action and version supplies more details of that action. Let's go with `object_detection/person_vehicle_bike`. Now we need to choose a media source. We recommend the [IoT Devkit sample videos](https://github.com/intel-iot-devkit/sample-videos) to get started. As the pipeline version indicates support for detecting people, person-bicycle-car-detection.mp4 would be a good choice.
> **Note:** Make sure to include `raw=true` parameter in the Github URL as shown in our examples. Failure to do so will result in a pipeline execution error.

pipeline_client offers a `run` command that takes two additional arguments the `pipeline` and the `uri` for the media source. The `run` command displays inference results until either the media is exhausted or `CTRL+C` is pressed.

Inference result bounding boxes are displayed in the format `label (confidence) [top left width height] {meta-data}` provided applicable data is present. At the end of the pipeline run, the average fps is shown.

```bash
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```

```text
Timestamp 48583333333
- vehicle (0.95) [0.00, 0.12, 0.15, 0.36]
Timestamp 48666666666
- vehicle (0.79) [0.00, 0.12, 0.14, 0.36]
Timestamp 48833333333
- vehicle (0.68) [0.00, 0.13, 0.11, 0.36]
Timestamp 48916666666
- vehicle (0.78) [0.00, 0.13, 0.10, 0.36]
Timestamp 49000000000
- vehicle (0.63) [0.00, 0.13, 0.09, 0.36]
Timestamp 49083333333
- vehicle (0.63) [0.00, 0.14, 0.07, 0.35]
Timestamp 49166666666
- vehicle (0.69) [0.00, 0.14, 0.07, 0.35]
Timestamp 49250000000
- vehicle (0.64) [0.00, 0.14, 0.05, 0.34]
avg_fps: 39.66
```

> **NOTE:** Inference results are not obtained via a REST API but read from an output file.
The file path is specified in the `destination` section of the REST request and will be discussed in a later section.

## Pipeline States

### Queued, Running and Completed

The pipeline_client `run` command starts the pipeline. The underlying REST request returns a `pipeline instance` which is used to query the state of the pipeline.
All being well it will go into `QUEUED` then `RUNNING` state. We can interrogate the pipeline status by using the pipeline_client `start` command that kicks off the pipeline like `run` and then exits displaying the `pipeline instance` (a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)) which is used by the `status` command to view pipeline state.
> **NOTE:** The pipeline instance value depends on the number of pipelines started while the server is running so may differ from the value shown in the following examples.

```bash
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```

```text
<snip>
Starting pipeline object_detection/person_vehicle_bike, instance = d83502e3ef314e8fbec8dc926eadd0c2
```

You will need both the pipeline tuple and `instance` id for the status command. This command will display pipeline state:

```bash
./client/pipeline_client.sh status object_detection/person_vehicle_bike d83502e3ef314e8fbec8dc926eadd0c2
```

```text
<snip>
RUNNING (49fps)
```

Then wait for a minute or so and try again. Pipeline will be completed.

```bash
./client/pipeline_client.sh status object_detection/person_vehicle_bike d83502e3ef314e8fbec8dc926eadd0c2
```

```text
<snip>
COMPLETED (50fps)
```

### Aborted

If a pipeline is stopped, rather than allowed to complete, it goes into the ABORTED state.
Start the pipeline again, this time we'll stop it.

```bash
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```

```text
<snip>
Starting pipeline object_detection/person_vehicle_bike, instance = 8ad2c85af4bd473e8a693aff562be316
```

```bash
./client/pipeline_client.sh status object_detection/person_vehicle_bike 8ad2c85af4bd473e8a693aff562be316
```

```text
<snip>
RUNNING (50fps)
```

```bash
./client/pipeline_client.sh stop object_detection/person_vehicle_bike 8ad2c85af4bd473e8a693aff562be316
```

```text
<snip>
Stopping Pipeline...
Pipeline stopped
avg_fps: 24.33
```

```bash
./client/pipeline_client.sh status object_detection/person_vehicle_bike 8ad2c85af4bd473e8a693aff562be316
```

```text
<snip>
ABORTED (47fps)
```

### Error

The error state covers a number of outcomes such as the request could not be satisfied, a pipeline dependency was missing or an initialization problem. We can create an error condition by supplying a valid but unreachable uri.

```bash
./client/pipeline_client.sh start object_detection/person_vehicle_bike http://bad-uri
```

```text
<snip>
Starting pipeline object_detection/person_vehicle_bike, instance = 2bb2d219310a4ee881faf258fbcc4355
```

Note that the Pipeline Server does not report an error at this stage as it goes into `QUEUED` state before it realizes that the source is not providing media.
Checking on state a few seconds later will show the error.

```bash
./client/pipeline_client.sh status object_detection/person_vehicle_bike 2bb2d219310a4ee881faf258fbcc4355
```

```text
<snip>
ERROR (0fps)
```

# Request Customizations

## Change Pipeline and Source Media

With pipeline_client it is easy to customize service requests. Here will use a vehicle classification pipeline `object_classification/vehicle_attributes` with the IoT Devkit video `car-detection.mp4`. Note how pipeline_client now displays classification metadata including type and color of vehicle.

```bash
./client/pipeline_client.sh run object_classification/vehicle_attributes https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true
```

```text
Starting pipeline object_classification/vehicle_attributes, instance = <uuid>
Pipeline running
<snip>
Timestamp 18080000000
- vehicle (1.00) [0.41, 0.00, 0.57, 0.33] {'color': 'red', 'type': 'car'}
Timestamp 18160000000
- vehicle (1.00) [0.41, 0.00, 0.57, 0.31] {'color': 'red', 'type': 'car'}
- vehicle (0.50) [0.09, 0.92, 0.27, 1.00] {'color': 'white', 'type': 'van'}
Timestamp 18240000000
- vehicle (1.00) [0.40, 0.00, 0.57, 0.27] {'color': 'red', 'type': 'car'}
Timestamp 18320000000
- vehicle (1.00) [0.40, 0.00, 0.56, 0.24] {'color': 'red', 'type': 'car'}
Timestamp 18400000000
- vehicle (1.00) [0.40, 0.00, 0.56, 0.22] {'color': 'red', 'type': 'car'}
- vehicle (0.53) [0.52, 0.19, 0.98, 0.99] {'color': 'black', 'type': 'truck'}
Timestamp 18480000000
- vehicle (0.99) [0.40, 0.00, 0.56, 0.20] {'color': 'red', 'type': 'car'}
- vehicle (0.81) [0.69, 0.00, 1.00, 0.36] {'color': 'black', 'type': 'bus'}
Timestamp 18560000000
- vehicle (1.00) [0.40, 0.00, 0.55, 0.18] {'color': 'red', 'type': 'car'}
- vehicle (0.71) [0.70, 0.00, 1.00, 0.36] {'color': 'black', 'type': 'bus'}
Timestamp 18640000000
- vehicle (0.98) [0.40, 0.00, 0.55, 0.15] {'color': 'red', 'type': 'car'}
```

If you look at the video, you can see that there are some errors in classification - there are no trucks or buses in the video. However you can see that associated confidence is much lower than the correct classification of the white and red cars.

## Change Inference Accelerator Device

Inference accelerator devices can be easily selected using the device parameter. Here we run the car classification pipeline again,
but this time use the integrated GPU for detection inference by setting the `detection-device` parameter.

```bash
./client/pipeline_client.sh run object_classification/vehicle_attributes https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true --parameter detection-device GPU --parameter detection-model-instance-id person_vehicle_bike_detection_gpu
```

```text
Starting pipeline object_classification/vehicle_attributes, instance = <uuid>
```

> **Note:** The GPU inference plug-in dynamically builds OpenCL kernels when it is first loaded resulting in a ~30s delay before inference results are produced.

> **Note:** The `detection-model-instance-id` parameter caches the GPU model with a unique id. For more information read about [model instance ids](docs/defining_pipelines.md#model-persistance-in-openvino-gstreamer-elements).

pipeline_client's fps measurement is useful when assessing pipeline performance with different accelerators.

## Visualize Inference
Pipeline server allows you to optionally visualize inference results using either [Real Time Streaming Protocol (RTSP)](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol) or [Web Real Time Communication (WebRTC)](https://webrtc.org/) by configuring the frame destination section of the request.

RTSP is simpler to set up but you must have an RTSP player (e.g. [VLC](https://www.videolan.org/vlc/)) to render output. WebRTC setup is more complex (e.g., requires additional server-side microservices) but has the upside of using a web browser for client visualization.

Before requesting visualization, the corresponding feature must be enabled in the server, see [Visualizing Inference Output](docs/running_pipeline_server.md#visualizing-inference-output).

### RTSP

RTSP allows you to connect to a server and display a video stream. The Pipeline Server includes an RTSP server that creates a stream that shows the incoming video with superimposed bounding boxes and meta-data. You will need a client that connects to the server and displays the video. We recommend [vlc](https://www.videolan.org/).

First start the Pipeline Server with RTSP enabled. By default, the RTSP stream will use port 8554.
```
docker/run.sh --enable-rtsp -v /tmp:/tmp
```

Then start pipeline and visualize as per [RTSP section in Customizing Pipeline Requests](docs/customizing_pipeline_requests.md#rtsp).

> **Note:** The pipeline must be running before you hit play otherwise VLC will not be able to connect to the RTSP server. For shorter video files you should have VLC ready to go before starting pipeline otherwise by the time you hit play the pipeline will have completed and the RTSP server will have shut down.

### WebRTC

WebRTC is more complex. Follow setup instructions in the [sample](samples/webrtc). More details on fine tuning request can be found in the [WebRTC section in Customizing Pipeline Requests](docs/customizing_pipeline_requests.md#webrtc).

## View REST Request

As the previous example has shown, the pipeline_client application works by converting command line arguments into Pipeline Server REST requests.
The `--show-request` option displays the REST verb, uri and body in the request.
Let's repeat the previous GPU inference example, adding RTSP output and show the underlying request.

```bash
./client/pipeline_client.sh run object_classification/vehicle_attributes https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true --parameter detection-device GPU --rtsp-path pipeline-server --show-request
```

```text
<snip>
POST http://localhost:8080/pipelines/object_classification/vehicle_attributes
Body:{'source': {'uri': 'https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true', 'type': 'uri'}, 'destination': {'metadata': {'type': 'file', 'path': '/tmp/results.jsonl', 'format': 'json-lines'}, 'frame': {'type': 'rtsp', 'path': 'pipeline-server'}}, 'parameters': {'detection-device': 'GPU'}}
```

The REST request is broken into three parts

1. VERB: `POST`
2. URI: `http://localhost:8080/pipelines/object_classification/vehicle_attributes`
3. BODY: `{"source": {"uri": ...`

The uri is easy to decode. It's the service address, `pipelines` command and the pipeline tuplet. The body contains three components:

1. The media source
2. The frame and metadata destinations
3. Pipeline parameters.

They are easier to understand when the json is pretty-printed

```bash
{
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "metadata": {
      "type": "file",
      "path": "/tmp/results.jsonl",
      "format": "json-lines"
    },
    "frame": {
      "type": "rtsp",
      "path": "pipeline-server"
    }
  },
  "parameters": {
    "detection-device": "GPU"
  }
}
```

1. Media source: type is `uri` and the uri is the car-detection.mp4 video
2. Destinations:
   * metadata: this is the inference results, they are sent to file `/tmp/results.jsonl` in `json-lines` format. pipeline_client parses this file to display the inference results and metadata.
   * frames: this the watermarked frames. Here they are sent to the RTSP server and available over given endpoint `pipeline-server`.
3. Parameters set pipeline properties. See the [Defining Pipelines](docs/defining_pipelines.md) document for more details on parameters.

The `--show-request` output can be easily converted int a curl command.

```bash
curl <URI> -X <VERB> -H "Content-Type: application/json' -d <BODY>
```

So the above request would be as below. Note the pipeline instance `1` returned by the request.

```bash
curl localhost:8080/pipelines/object_classification/vehicle_attributes -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "metadata": {
      "type": "file",
      "path": "/tmp/results.jsonl",
      "format": "json-lines"
    },
    "frame": {
      "type": "rtsp",
      "path": "pipeline-server"
    }
  },
  "parameters": {
    "detection-device": "GPU"
  }
}'
```

```text
59896b90853511ec838b0242ac110002
```

# Changing Pipeline Model

The Pipeline Server makes pipeline customization and model selection a simple task. The [Changing Object Detection Models Tutorial](docs/changing_object_detection_models.md) provides step by step instructions for changing the object detection reference pipeline to use a model better suited to a different video source.

# Further Reading

| **Documentation** | **Reference Guides** | **Tutorials** |
| ------------    | ------------------ | ----------- |
| **-** [Defining Media Analytics Pipelines](docs/defining_pipelines.md) <br/> **-** [Building Intel® DL Streamer Pipeline Server](docs/building_pipeline_server.md) <br/> **-** [Running Intel® DL Streamer Pipeline Server](docs/running_pipeline_server.md) <br/> **-** [Customizing Pipeline Requests](docs/customizing_pipeline_requests.md) <br/> **-** [Creating Extensions](docs/creating_extensions.md)| **-** [Intel® DL Streamer Pipeline Server Architecture Diagram](docs/images/pipeline_server_architecture.png) <br/> **-** [Microservice Endpoints](docs/restful_microservice_interfaces.md) <br/> **-** [Build Script Reference](docs/build_script_reference.md) <br/> **-** [Run Script Reference](docs/run_script_reference.md) <br/> **-** [Pipeline Client Reference](client/README.md)| **-** [Changing Object Detection Models](docs/changing_object_detection_models.md) <br/> **-** [Kubernetes Deployment with Load Balancing](samples/kubernetes/README.md)

## Related Links

| **Media Frameworks** | **Media Analytics** | **Samples and Reference Designs**
| ------------    | ------------------ | -----------------|
| **-** [GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* <br/> **-** [GStreamer* Overview](docs/gstreamer_overview.md) <br/> **-** [FFmpeg](https://ffmpeg.org/)* | **-** [Intel® Deep Learning Streamer Pipeline Framework](https://github.com/dlstreamer/dlstreamer) <br/> **-** [OpenVINO<sup>&#8482;</sup> Toolkit](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit.html) <br/> **-** [FFmpeg* Video Analytics](https://github.com/VCDP/FFmpeg-patch) | **-** [Open Visual Cloud Smart City Sample](https://github.com/OpenVisualCloud/Smart-City-Sample) <br/> **-** [Open Visual Cloud Ad Insertion Sample](https://github.com/OpenVisualCloud/Ad-Insertion-Sample) <br/> **-** [Edge Insights for Retail](https://software.intel.com/content/www/us/en/develop/articles/real-time-sensor-fusion-for-loss-detection.html)

# Known Issues

Known issues are tracked on [GitHub](https://github.com/dlstreamer/pipeline-server/issues)*

---
\* Other names and brands may be claimed as the property of others.
