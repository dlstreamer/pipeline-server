# Running Video Analytics Serving
| [Video Analytics Serving Microservice](#video-analytics-serving-microservice) | [Interacting with the Microservice](#interacting-with-the-microservice) | [Selecting Pipelines and Models at Runtime](#selecting-pipelines-and-models-at-runtime) | [Developer Mode](#developer-mode) | 

Video Analytics Serving docker images can be started using standard `docker run` and `docker compose` commands. For convenience a simplified run script is provided to pass common options to `docker
run` such as proxies, device mounts, and to expose the default microservice port (8080).

The following sections give an overview of the way the
image is run as well as common customization and interaction patterns.

> **Note:** Descriptions and instructions below assume a working
> knowledge of docker commands and features. For more information
> see docker [documentation](https://docs.docker.com/get-started/).

# Video Analytics Serving Microservice

The default image of Video Analytics Serving includes a microservice
that exposes a RESTful interface on port
8080.  The microservice has endpoints to list, start, stop, and get
the status of media analytics pipelines.

## Microservice Endpoints 

| Path | Description |
|----|------|
| [`GET` /models](restful_microservice_interfaces.md#get-models) | Return supported models. |
| [`GET` /pipelines](restful_microservice_interfaces.md#get-pipelines) | Return supported pipelines. |
| [`GET` /pipelines/{name}/{version}](restful_microservice_interfaces.md#get-pipelinesnameversion)  | Return pipeline description.|
| [`POST` /pipelines/{name}/{version}](restful_microservice_interfaces.md#post-pipelinesnameversion) | Start new pipeline instance. |
| [`GET` /pipelines/{name}/{version}/{instance_id}](restful_microservice_interfaces.md#get-pipelinesnameversioninstance_id) | Return pipeline instance summary. |
| [`GET` /pipelines/{name}/{version}/{instance_id}/status](restful_microservice_interfaces.md#get-pipelinesnameversioninstance_idstatus) | Return pipeline instance status. |
| [`DELETE` /pipelines/{name}/{version}/{instance_id}](restful_microservice_interfaces.md#delete-pipelinesnameversioninstance_id) | Stops a running pipeline or cancels a queued pipeline. |

## Default Run Commands and Image Names

| Command | Media Analytics Base Image | Image Name | Description |
| ---     | ---        | --- | ----        |
| `./docker/run.sh`|**DL Streamer** docker [file](https://github.com/opencv/gst-video-analytics/blob/preview/audio-detect/docker/Dockerfile) |`video-analytics-serving-gstreamer` | DL Streamer based microservice with default pipeline definitions and deep learning models. Exposes port 8080. Mounts the host system's graphics devices. |
| `./docker/run.sh --framework ffmpeg`| **FFmpeg Video Analytics** docker [file](https://github.com/VCDP/FFmpeg-patch/blob/ffmpeg4.2_va/docker/Dockerfile.source) |`video-analytics-serving-ffmpeg`| FFmpeg Video Analytics based microservice with default pipeline definitions and deep learning models. Mounts the graphics devices. |         


# Interacting with the Microservice

The following examples demonstrate how to start and issue requests to
a Video Analytics Serving Microservice either using the `GStreamer`
based image or the `FFmpeg` based image.

> **Note:** The following examples assume that the Video Analytics
> Serving image has already been built. For more information and
> instructions on building please see the [Getting Started
> Guide](../README.md) or [Building Video Analytics Serving Docker
> Images](../docs/building_video_analytics_serving.md)

> **Note:** Both the `GStreamer` based microservice and the `FFmpeg`
> based microservice use the same default port: `8080` and only one
> can be started at a time. To change the port please see the command
> line options for the Video Analytics Serving microservice.
>

## Starting the Microservice

To start the microservice use standard `docker run` commands via the
provided utility script.

### GStreamer Video Analytics based Microservice

#### DL Streamer Base Image Microservice
**Example:**

```bash
$ docker/run.sh -v /tmp:/tmp
```

#### Open Visual Cloud Base Image or OpenVINO<sup>&#8482;</sup> Base Image Microservice
Base image doesn't include gvaaudiodetect element, ignoring missing gvaaudiodetect element error at run time.
**Example:**

```bash
$ docker/run.sh -v /tmp:/tmp -e IGNORE_INIT_ERRORS=True
```

### FFmpeg Video Analytics based Microservice
**Example:**

```bash
$ docker/run.sh --framework ffmpeg -v /tmp:/tmp
```

## Issuing Requests

From a new shell use curl to issue requests to the running
microservice.

### Getting Loaded Pipelines
**Example:** 

```bash
$ curl localhost:8080/pipelines
[
  {
    "description": "Object Detection Pipeline",
    "name": "object_detection",
    <snip>
    "type": "GStreamer",
    "version": "1"
  },
  {
    "description": "Emotion Recognition Pipeline",
    "name": "emotion_recognition",
    <snip>
    "type": "GStreamer",
    "version": "1"
  }
]
```

### Detecting Objects in a Sample Video File
**Example:**

```bash
curl localhost:8080/pipelines/object_detection/1 -X POST -H \
'Content-Type: application/json' -d \
'{ 
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "type": "file",
    "path": "/tmp/results.txt",
    "format": "json-lines"
  }
}'
$ tail -f /tmp/results.txt
{"objects":[{"detection":{"bounding_box":{"x_max":0.8810903429985046,"x_min":0.77934330701828,"y_max":0.8930767178535461,"y_min":0.3040514588356018},"confidence":0.5735679268836975,"label":"bottle","label_id":5},"h":213,"roi_type":"bottle","w":65,"x":499,"y":109}],"resolution":{"height":360,"width":640},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true","timestamp":972067039}
```

Detection results are published to `/tmp/results.txt`.

## Stopping the Microservice

To stop the microservice use standard `docker stop` or `docker
kill` commands with the name of the running container.


### DL Streamer based Microservice
**Example:**

```bash
$ docker stop video-analytics-serving-gstreamer
```

### FFmpeg Video Analytics based Microservice
**Example:**
```bash
$ docker stop video-analytics-serving-ffmpeg
```

# Selecting Pipelines and Models at Runtime

The models and pipelines loaded by the Video Analytics Serving
microservice can be selected at runtime by volume mounting the
appropriate directories when starting the container.

> **Note:** Mounted pipeline definitions must match the media
> framework supported in the media analytics base image.

> **Note:** Pipeline and Model directories are only scanned once at
> service start-up. To make modifications the service must be
> restarted.

### Mounting Pipelines and Models into a DL Streamer based Image
**Example:**

```bash
$ ./docker/run.sh --framework gstreamer --pipelines /path/to/my-pipelines --models /path/to/my-models
```

# Developer Mode

The run script includes a `--dev` flag which starts the
container in "developer" mode. "Developer mode," sets `docker run`
options to make development and modification of media analytics
pipelines easier. 

> **Note:** Pipeline and Model directories are only scanned once at
> service start-up. When making modifications to the models,
> pipelines, or source code the service must be restarted for them to
> take effect.

Developer mode:

* Starts the container with an interactive bash shell.
* Volume mounts the local source code, models and pipelines
  directories. Any changes made to the local files are immediately
  reflected in the running container.
* Uses the docker option `--network=host`. All ports and network interfaces for the host are shared with the container.
* Uses the docker option `--privileged`. Operates the container with elevated privileges.

### DL Streamer based Image in Developer Mode
**Example:**

```bash
$ docker/run.sh --dev
vaserving@my-host:~$ python3 -m vaserving 
```

---
\* Other names and brands may be claimed as the property of others.




