# Video Analytics Serving

Video Analytics Serving provides the structure and key components needed to bootstrap development of visual processing solutions. Video Analytics Serving has been designed to simplify the deployment and use of hardware optimized video analytics pipelines. A reference service implementation exposes RESTful interfaces that make use of example pipelines to get you started.

These endpoints and pipelines may be customized to negotiate the inputs and outputs appropriate to many use cases. Developers may choose to customize and then execute pre-defined video analytics (VA) pipelines in either [GStreamer](https://github.com/opencv/gst-video-analytics/wiki)
 or [FFmpeg](https://github.com/OpenVisualCloud/Dockerfiles/blob/master/doc/ffmpeg.md).

 Each VA pipeline type defines the semantics of its customizable parameters. These parameters are included in requests to start a pipeline and will influence the runtime behavior of a VA pipeline. In this way VA pipeline developers may define named and versioned VA pipelines and expose them to users via simple RESTful interfaces.

## Architecture Overview
<img src="doc/html/image/video_analytics_service_architecture.png" width="800">


### DISCLAIMER
**IMPORTANT:** Video Analytics Serving is provided as a pre-production _sample_.

The project provides a reference architecture with straightforward examples to accelerate your implementation of a solution. However, it is **_not intended for production without modification_**. In addition to modifying pipelines and models to fit your use cases, you must harden security of endpoints and other critical tasks to secure your solution.

## Interfaces

| Path | Description |
|----|------|
| [`GET` /models](interfaces.md#get-models) | Return supported models. |
| [`GET` /pipelines](interfaces.md#get-pipelines) | Return supported pipelines |
| [`GET` /pipelines/{name}/{version}](interfaces.md#get-pipelinesnameversion)  | Return pipeline description.|
| [`POST` /pipelines/{name}/{version}](interfaces.md#post-pipelinesnameversion) | Start new pipeline instance. |
| [`GET` /pipelines/{name}/{version}/{instance_id}](interfaces.md#get-pipelinesnameversioninstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/{name}/{version}/{instance_id}/status](interfaces.md#get-pipelinesnameversioninstance_idstatus) | Return pipeline instance status. |

## Example Pipelines

Video Analytics Serving includes two [sample](pipelines) analytics pipelines for GStreamer and FFmpeg. The GStreamer sample pipelines use [plugins](https://github.com/opencv/gst-video-analytics) for CNN model-based video analytics utilizing [Intel OpenVino](https://software.intel.com/en-us/openvino-toolkit). When building with Docker, these plugins will be built and installed inside the Docker image. You can find documentation on the properties of these elements [here](https://github.com/opencv/gst-video-analytics/wiki/Elements).

|Pipeline| Description| Example Request| Example Detection|
|--------|------------|----------------|------------------|
|/pipelines/object_detection/1|Object Detection|curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "uri": "file:///tmp/results.txt"}}'|{"objects": [{"detection": {"bounding_box": {"x_max": 0.8820319175720215, "x_min": 0.7787219285964966, "y_max": 0.8876367211341858, "y_min": 0.3044118285179138}, "confidence": 0.6628172397613525, "label": "bottle", "label_id": 5}}], "resolution": {"height": 360, "width": 640}, "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "timestamp": 7407821229}|
|/pipelines/emotion_recognition/1|Emotion Recognition|curl localhost:8080/pipelines/emotion_recognition/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/head-pose-face-detection-male.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "uri": "file:///tmp/results1.txt"}}'|{"objects": [{"detection": {"bounding_box": {"x_max": 0.5859826803207397, "x_min": 0.43868017196655273, "y_max": 0.5278626084327698, "y_min": 0.15201044082641602}, "confidence": 0.9999998807907104, "label": "face", "label_id": 1}, "emotion": {"label": "neutral", "model": {"name": "0003_EmoNet_ResNet10"}}}], "resolution": {"height": 432, "width": 768}, "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/head-pose-face-detection-male.mp4?raw=true", "timestamp": 133083333333}|

## Install Docker

(1) Install [docker engine](https://docs.docker.com/install).     
(2) Install [docker compose](https://docs.docker.com/compose/install), if you plan to deploy through docker compose. Version 1.20+ is required.

## Build and Run Video Analytics Serving

Video Analytics Serving may be modified to co-exist in a container alongside other applications or can be built and run as a standalone service.

### Building

To get started, build the service as a standalone component execute the following command

```bash
./build.sh
```

### Running

After the service is built it can be run using standard docker run commands (volume mounting is required only to see the sample results)

```bash
(1) sudo docker run -e http_proxy=$http_proxy -e https_proxy=$https_proxy -p 8080:8080 -v /tmp:/tmp --rm video_analytics_service_gstreamer
```

### Sample Request

With the service running, initiate a request to start a pipeline using the following commands.
```bash
(1) curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "uri": "file:///tmp/results.txt"}}'

(2) tail -f /tmp/results.txt
```
### Sample Result
```
{"objects": [{"detection": {"bounding_box": {"x_max": 0.9027906656265259, "x_min": 0.792841911315918, "y_max": 0.8914870023727417, "y_min": 0.3036404848098755}, "confidence": 0.6788424253463745, "label": "bottle", "label_id": 5}}], "resolution": {"height": 360, "width": 640}, "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "timestamp": 39854748603}
```
