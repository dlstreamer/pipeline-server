# Running Video Analytics Serving
| [Video Analytics Serving Microservice](#video-analytics-serving-microservice) | [Interacting with the Microservice](#interacting-with-the-microservice) | [Real Time Streaming Protocol (RTSP) Re-streaming](#real-time-streaming-protocol-rtsp-re-streaming) | [Selecting Pipelines and Models at Runtime](#selecting-pipelines-and-models-at-runtime) | [Developer Mode](#developer-mode) | [Enabling Hardware Accelerators](#enabling-hardware-accelerators) |

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
a Video Analytics Serving Microservice either using the `DL Streamer`
based image or the `FFmpeg` based image.

> **Note:** The following examples assume that the Video Analytics
> Serving image has already been built. For more information and
> instructions on building please see the [Getting Started
> Guide](../README.md) or [Building Video Analytics Serving Docker
> Images](../docs/building_video_analytics_serving.md)

> **Note:** Both the `DL Streamer` based microservice and the `FFmpeg`
> based microservice use the same default port: `8080` and only one
> can be started at a time. To change the port please see the command
> line options for the Video Analytics Serving microservice.
>

## Starting the Microservice

To start the microservice use standard `docker run` commands via the
provided utility script.

### DL Streamer based Microservice
**Example:**
```bash
docker/run.sh -v /tmp:/tmp
```

### FFmpeg Video Analytics based Microservice
**Example:**

```bash
docker/run.sh --framework ffmpeg -v /tmp:/tmp
```

## Issuing Requests

From a new shell use curl to issue requests to the running
microservice.

### Getting Loaded Pipelines
**Example:**
> **Note:** In this example we assume you are running FFmpeg Video Analytics based Microservice
```bash
curl localhost:8080/pipelines
```
```
[
  {
    "description": "Object Detection Pipeline",
    "name": "object_detection",
    <snip>
    "type": "FFmpeg",
    "version": "1"
  },
  {
    "description": "Emotion Recognition Pipeline",
    "name": "emotion_recognition",
    <snip>
    "type": "FFmpeg",
    "version": "1"
  }
]
```

### Detecting Objects in a Sample Video File
**Example:**
> **Note:** In this example we assume you are running DL Streamer based Microservice
```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "metadata": {
      "type": "file",
      "path": "/tmp/results.txt",
      "format": "json-lines"
    }
  }
}'
```
```
tail -f /tmp/results.txt
```
```
{"objects":[{"detection":{"bounding_box":{"x_max":0.0503933560103178,"x_min":0.0,"y_max":0.34233352541923523,"y_min":0.14351698756217957},"confidence":0.6430817246437073,"label":"vehicle","label_id":2},"h":86,"roi_type":"vehicle","w":39,"x":0,"y":62}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":49250000000}
```

Detection results are published to `/tmp/results.txt`.

## Stopping the Microservice

To stop the microservice use standard `docker stop` or `docker
kill` commands with the name of the running container.


### DL Streamer based Microservice
**Example:**

```bash
docker stop video-analytics-serving-gstreamer
```

### FFmpeg Video Analytics based Microservice
**Example:**
```bash
docker stop video-analytics-serving-ffmpeg
```

# Real Time Streaming Protocol (RTSP) Re-streaming
> **Note:** RTSP Re-streaming supported only in DL Streamer based Microservice.

VA Serving contains an [RTSP](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol) server that can be optionally started at launch time. This allows an RTSP client to connect and visualize input video with superimposed bounding boxes.

### Enable RTSP in service
```bash
docker/run.sh --enable-rtsp
```
> **Note:** RTSP server starts at service start-up for all pipelines. It uses port 8554 and has been tested with [VLC](https://www.videolan.org/vlc/index.html).

### Connect and visualize
> **Note:** Leverage REST client when available.

*  Start a pipeline with curl request with frame destination set as rtsp and custom path set. For demonstration, path set as `person-detection` in example request below.
```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "metadata": {
      "type": "file",
      "path": "/tmp/results.txt",
      "format": "json-lines"
    },
    "frame": {
      "type": "rtsp",
      "path": "person-detection"
    }
  }
}'
```
*  Check that pipeline is running using [status request](restful_microservice_interfaces.md#get-pipelinesnameversioninstance_id) before trying to connect to the RTSP server.
*  Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/person-detection`.

### RTSP destination params.
```bash
"frame": {
  "type": "rtsp",
  "path" : <custom rtsp path>(required. When path already exists, throws error)
}
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
./docker/run.sh --framework gstreamer --pipelines /path/to/my-pipelines --models /path/to/my-models
```

# Enabling Hardware Accelerators
The run script automatically gives docker access (i.e. device, volume mount and device cgroup rule) to the following accelerators
* iGPU
* Intel&reg; Neural Compute Stick 2 (NCS2)
* HDDL-R cards

You also need to specify the inference device in the parameters section
of the VA Serving request. Example for GPU below
```json
"parameters": {
   "device": "GPU"
}
```
See [Customizing Pipeline Requests](customizing_pipeline_requests.md) for more information.

The following the table shows docker configuration and inference device name for all accelerators.
> **Note:** Open Visual Cloud base images only support the GPU accelerator.
> OpenVINO base images support all accelerators.

|Accelerator| Device      | Volume Mount(s)    |CGroup Rule|Inference Device|
|-----------|-------------|------------------- |-----------|----------------|
| GPU       | /dev/dri    |                    |           | GPU            |
| NCS2      |             | /dev/bus/usb       |c 189:* rmw| MYRIAD         |
| HDDL-R    |             | /var/tmp, /dev/shm |           | HDDL           |

> **Note:** NCS2 and HDDL-R accelerators are incompatible and cannot be used on the same system.

## GPU
The first time inference is run on a GPU there will be a 30s delay while OpenCL kernels are built for the specific device. To prevent the same delay from occurring on subsequent runs a [model instance id](docs/defining_pipelines.md#model-persistance-in-openvino-gstreamer-elements) can be specified in the request.

On Ubuntu20 and later hosts [extra configuration](https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md), not shown in the above table, is necessary to allow access to the GPU. The [docker/run.sh](../docker/run.sh) script takes care of this for you, but other deployments will have to be updated accordingly.

## NCS2

Configure your host by following the steps outlined in the OpenVINO [documentation](https://docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_linux.html#additional-NCS-steps)

> **Note:** These steps require the file `97-myriad-usbboot.rules` which can be extracted from the Video Analytics Serving docker container using the following command:
```bash
./docker/run.sh -v ${PWD}:/tmp --entrypoint cp --entrypoint-args "/opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /tmp"
```
> Once extracted the file will be in the current directory. Follow the instructions given in the OpenVINO documentation to copy it to the correct location.

## HDDL-R
Configure your host by downloading the [HDDL driver package](https://storage.openvinotoolkit.org/drivers/vpu/hddl/2021.4.2/hddl_ubuntu20_1886.tgz) then installing dependencies and run the hddldaemon on the host as per the [HDDL install guide](https://github.com/openvinotoolkit/docker_ci/blob/releases/2021/4/install_guide_vpu_hddl.md).

> The HDDL plug-in in the container communicates with the daemon on the host, so the daemon must be started before running the container.

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
docker/run.sh --dev
```
```
vaserving@my-host:~$ python3 -m vaserving
```

---
\* Other names and brands may be claimed as the property of others.
