# Video Analytics Serving

Video Analytics Serving simplifies the deployment and use of hardware optimized video analytics pipelines. It offers developers a simple way to create RESTful APIs  to start, stop, enumerate and customize pre-defined pipelines using either [GStreamer](https://github.com/opencv/gst-video-analytics/wiki)
 or [FFmpeg](https://github.com/OpenVisualCloud/Dockerfiles/blob/master/doc/ffmpeg.md). Developers create pipeline templates using their framework of choice and Video Analytics Serving manages launching pipeline instances based on incoming requests.

> **IMPORTANT:** Video Analytics Serving is provided as a _sample_. It is not intended to be deployed into production environments without modification. Developers deploying Video Analytics Serving should review it against their production requirements.

## Architecture Overview
<img src="docs/images/video_analytics_service_architecture.png" width="800">

## Interfaces

| Path | Description |
|----|------|
| [`GET` /models](interfaces.md#get-models) | Return supported models. |
| [`GET` /pipelines](interfaces.md#get-pipelines) | Return supported pipelines. |
| [`GET` /pipelines/{name}/{version}](interfaces.md#get-pipelinesnameversion)  | Return pipeline description.|
| [`POST` /pipelines/{name}/{version}](interfaces.md#post-pipelinesnameversion) | Start new pipeline instance. |
| [`GET` /pipelines/{name}/{version}/{instance_id}](interfaces.md#get-pipelinesnameversioninstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/{name}/{version}/{instance_id}/status](interfaces.md#get-pipelinesnameversioninstance_idstatus) | Return pipeline instance status. |
| [`DELETE` /pipelines/{name}/{version}/{instance_id}](interfaces.md#delete-pipelinesnameversioninstance_id) | Stops a running pipeline or cancels a queued pipeline. |

## Building and Running
Video Analytics Serving can be configured as a microservice or used as a
library within another application. The following steps demonstrate
how to quickly deploy a uService with sample pipelines and models.

More information on customizing, building and running Video Analytics
Serving docker images can be found in the [working with docker](docs/working_with_docker.md) documentation.

### Prerequisites
(1) Install [docker engine](https://docs.docker.com/install).  
(2) Install [docker compose](https://docs.docker.com/compose/install), if you plan to deploy through docker compose. Version 1.20+ is required.


### Building
To get started, build the service as a standalone component execute the following command:
```bash
./docker/build.sh
```

### Running
After a successful build, run the service using the included script:
```bash
./docker/run.sh -v /tmp:/tmp
```

This script issues a standard docker run command to launch the container. Volume mounting is used to publish the sample results to your host.

## Example Pipelines
Video Analytics Serving includes two [sample](pipelines) analytics pipelines for GStreamer and FFmpeg. The GStreamer sample pipelines use [plugins](https://github.com/opencv/gst-video-analytics) for CNN model-based video analytics utilizing [Intel OpenVino](https://software.intel.com/en-us/openvino-toolkit). When building with Docker, these plugins will be built and installed inside the Docker image. You can find documentation on the properties of these elements [here](https://github.com/opencv/gst-video-analytics/wiki/Elements).

|Pipeline| Description| Example Request| Example Detection|
|--------|------------|----------------|------------------|
|/pipelines/object_detection/1|Object Detection|curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'|{"objects":[{"detection":{"bounding_box":{"x_max":0.8810903429985046,"x_min":0.77934330701828,"y_max":0.8930767178535461,"y_min":0.3040514588356018},"confidence":0.5735679268836975,"label":"bottle","label_id":5},"h":213,"roi_type":"bottle","w":65,"x":499,"y":109}],"resolution":{"height":360,"width":640},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true","timestamp":972067039}|
|/pipelines/emotion_recognition/1|Emotion Recognition|curl localhost:8080/pipelines/emotion_recognition/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/head-pose-face-detection-male.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results1.txt", "format":"json-lines"}}'|{"objects":[{"detection":{"bounding_box":{"x_max":0.567557156085968,"x_min":0.42375022172927856,"y_max":0.5346322059631348,"y_min":0.15673652291297913},"confidence":0.9999996423721313,"label":"face","label_id":1},"emotion":{"label":"neutral","model":{"name":"0003_EmoNet_ResNet10"}},"h":163,"roi_type":"face","w":111,"x":325,"y":68}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/head-pose-face-detection-male.mp4?raw=true","timestamp":13333333333}
|/pipelines/audio_detection/1|Audio Detection|curl localhost:8080/pipelines/audio_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "file:///root/gst-video-analytics/samples/gst_launch/audio_detect/how_are_you_doing.wav", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results1.txt", "format":"json-lines"}}'|

### Sample Request

With the service running, initiate a request to start a pipeline using the following commands.
```bash
(1) curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'

(2) tail -f /tmp/results.txt
```

### Sample Result
```json
{"objects":[{"detection":{"bounding_box":{"x_max":0.8810903429985046,"x_min":0.77934330701828,"y_max":0.8930767178535461,"y_min":0.3040514588356018},"confidence":0.5735679268836975,"label":"bottle","label_id":5},"h":213,"roi_type":"bottle","w":65,"x":499,"y":109}],"resolution":{"height":360,"width":640},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true","timestamp":972067039}
```

