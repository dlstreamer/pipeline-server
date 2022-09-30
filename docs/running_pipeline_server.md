# Running Intel(R) DL Streamer Pipeline Server
| [Intel(R) DL Streamer Pipeline Server Microservice](#dlstreamer-pipeline-server-microservice) | [Interacting with the Microservice](#interacting-with-the-microservice) | [Real Time Streaming Protocol (RTSP) Re-streaming](#real-time-streaming-protocol-rtsp-re-streaming) | [Selecting Pipelines and Models at Runtime](#selecting-pipelines-and-models-at-runtime) | [Developer Mode](#developer-mode) | [Enabling Hardware Accelerators](#enabling-hardware-accelerators) |

Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server docker images can be started using standard `docker run` and `docker compose` commands. For convenience a simplified run script is provided to pass common options to `docker
run` such as proxies, device mounts, and to expose the default microservice port (8080).

The following sections give an overview of the way the
image is run as well as common customization and interaction patterns.

> **Note:** Descriptions and instructions below assume a working
> knowledge of docker commands and features. For more information
> see docker [documentation](https://docs.docker.com/get-started/).

# Intel(R) DL Streamer Pipeline Server Microservice

The default image of the Pipeline Server includes a microservice
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
| `./docker/run.sh`|**Intel(R) DL Streamer** docker [file](https://github.com/dlstreamer/dlstreamer/blob/master/docker/binary/ubuntu20/dlstreamer.Dockerfile) |`dlstreamer-pipeline-server-gstreamer` | Intel(R) DL Streamer based microservice with default pipeline definitions and deep learning models. Exposes port 8080. Mounts the host system's graphics devices. |
| `./docker/run.sh --framework ffmpeg`| **FFmpeg Video Analytics** docker [file](https://github.com/VCDP/FFmpeg-patch/blob/ffmpeg4.2_va/docker/Dockerfile.source) |`dlstreamer-pipeline-server-ffmpeg`| FFmpeg Video Analytics based microservice with default pipeline definitions and deep learning models. Mounts the graphics devices. |


# Interacting with the Microservice

The following examples demonstrate how to start and issue requests to
a Pipeline Server Microservice either using the `Intel(R) DL Streamer`
based image or the `FFmpeg` based image.

> **Note:** The following examples assume that the Pipeline Server image has already been built. For more information and
> instructions on building please see the [Getting Started
> Guide](../README.md) or [Building Intel(R) DL Streamer Pipeline Server Docker
> Images](../docs/building_pipeline_server.md)

> **Note:** Both the `Intel(R) DL Streamer` based microservice and the `FFmpeg`
> based microservice use the same default port: `8080` and only one
> can be started at a time. To change the port please see the command
> line options for the Pipeline Server microservice.
>

## Starting the Microservice

To start the microservice use standard `docker run` commands via the
provided utility script.

### Intel(R) DL Streamer based Microservice
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
> **Note:** In this example we assume you are running Intel(R) DL Streamer based Microservice
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


### Intel(R) DL Streamer based Microservice
**Example:**

```bash
docker stop dlstreamer-pipeline-server-gstreamer
```

### FFmpeg Video Analytics based Microservice
**Example:**
```bash
docker stop dlstreamer-pipeline-server-ffmpeg
```

# Visualizing Inference Output

> **Note:** This feature is supported only in the Intel(R) DL Streamer based Microservice.

There are two modes of visualization, [RTSP](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol) and [WebRTC](https://en.wikipedia.org/wiki/WebRTC).

## Underlying Protocols

RTSP and WebRTC are standards based definitions for rendering media output and facilitating **control** of stream activities (e.g., play, pause, rewind) by negotiating with remote clients about how data is to be authorized, packaged and streamed. However they are not responsible for transporting media data.

The actual **transfer** of the media data is governed by [Realtime Transport Protocol (RTP)](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol). RTP is essentially wrapping UDP to provide a level of reliability.

The [Session Description Protocol (SDP)](https://en.wikipedia.org/wiki/Session_Description_Protocol) is used by RTSP as a standardized way to understand session level **parameters** of the media stream (e.g., URI, session name, date/time session is available, etc.).

Real Time Control Protocol (RTCP) collects RTP **statistics** that are needed to measure throughput of streaming sessions.

## Real Time Streaming Protocol (RTSP)

The Pipeline Server contains an [RTSP](https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol) server that can be optionally started at launch time. This allows an RTSP client to connect and visualize input video with superimposed bounding boxes.

```bash
docker/run.sh --enable-rtsp
```

> **Note:** RTSP server starts at service start-up for all pipelines. It uses port 8554 and has been tested with [VLC](https://www.videolan.org/vlc/index.html).

## Web Real Time Communication (WebRTC)

The Pipeline Server contains support for [WebRTC](https://en.wikipedia.org/wiki/WebRTC) that allows viewing from any system on the current network right within your browser. This is enabled using an HTML5 video player and JavaScript APIs in the browser to negotiate with Pipeline Server. With these prerequisites provided as dependent microservices, it makes a very low bar for clients to render streams that show what is being detected by the running pipeline. This allows a user to connect and visualize input video with superimposed bounding boxes by navigating to a webserver that hosts the page with HTML5 video player and backed by JavaScript APIs. Has been tested with Chrome and Firefox, though [other browsers](https://html5test.com) are also supported.


```bash
docker/run.sh --enable-webrtc
```
> **Note:** WebRTC support starts at service start-up for all pipelines. It _requires_ a WebRTC signaling server container running on port 8443 and a web server container running on port 8082.

For details and launch instructions for prerequisites, refer to our [WebRTC sample](/samples/webrtc/README.md).

# Selecting Pipelines and Models at Runtime

The models and pipelines loaded by the Pipeline Server
microservice can be selected at runtime by volume mounting the
appropriate directories when starting the container.

> **Note:** Mounted pipeline definitions must match the media
> framework supported in the media analytics base image.

> **Note:** Pipeline and Model directories are only scanned once at
> service start-up. To make modifications the service must be
> restarted.

### Mounting Pipelines and Models into a Intel(R) DL Streamer based Image
**Example:**

```bash
./docker/run.sh --framework gstreamer --pipelines /path/to/my-pipelines --models /path/to/my-models
```

# Enabling Hardware Accelerators
The run script automatically gives docker access (i.e. device, volume mount and device cgroup rule) to the following accelerators
* iGPU
* Intel&reg; Neural Compute Stick 2 (Intel&reg; NCS2)
* HDDL-R cards

You also need to specify the inference device in the parameters section
of the Pipeline Server request. Example for GPU below
```json
"parameters": {
   "device": "GPU"
}
```
See [Customizing Pipeline Requests](customizing_pipeline_requests.md) for more information.

The following the table shows docker configuration and inference device name for all accelerators.
> **Note:** Open Visual Cloud base images only support the GPU accelerator.
> OpenVINO<sup>&#8482;</sup> base images support all accelerators.

|Accelerator| Device      | Volume Mount(s)    |CGroup Rule|Inference Device|
|-----------|-------------|------------------- |-----------|----------------|
| GPU       | /dev/dri/renderDxxx    |                    |           | GPU            |
| Intel&reg; NCS2      |             | /dev/bus/usb       |c 189:* rmw| MYRIAD         |
| HDDL-R    |             | /var/tmp, /dev/shm |           | HDDL           |

> **Note:** Intel&reg; NCS2 and HDDL-R accelerators are incompatible and cannot be used on the same system.

## GPU
The first time inference is run on a GPU there will be a 30s delay while OpenCL kernels are built for the specific device. To prevent the same delay from occurring on subsequent runs a [model instance id](docs/defining_pipelines.md#model-persistance-in-openvino-gstreamer-elements) can be specified in the request. You can also set the `cl_cache_dir` environment variable to specify location of kernel cache so it can be re-used across sessions.

If multiple GPUs are available, /dev/dri/renderD128 will be automatically selected. The environment variable [GST_VAAPI_DRM_DEVICE](https://gstreamer.freedesktop.org/documentation/vaapi/index.html?gi-language=python) will be set to device path. Different devices can be selected by using the `--gpu-device` argument.
```
--gpu-device /dev/dri/renderD129
```

On Ubuntu20 and later hosts [extra configuration](https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md), not shown in the above table, is necessary to allow access to the GPU. The [docker/run.sh](../docker/run.sh) script takes care of this for you, but other deployments will have to be updated accordingly.

## Intel&reg; NCS2

Configure your host by following the steps outlined in the OpenVINO<sup>&#8482;</sup> [documentation](https://docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_linux.html#additional-NCS-steps)

> **Note:** These steps require the file `97-myriad-usbboot.rules` which can be extracted from the Pipeline Server docker container using the following command:
```bash
./docker/run.sh -v ${PWD}:/tmp --entrypoint cp --entrypoint-args "/opt/intel/openvino/inference_engine/external/97-myriad-usbboot.rules /tmp"
```
> Once extracted the file will be in the current directory. Follow the instructions given in the OpenVINO<sup>&#8482;</sup> documentation to copy it to the correct location.

## HDDL-R
Configure your host by downloading the [HDDL driver package](https://storage.openvinotoolkit.org/drivers/vpu/hddl/2021.4.2/hddl_ubuntu20_1886.tgz) then installing dependencies and run the hddldaemon on the host as per the [HDDL install guide](https://github.com/openvinotoolkit/docker_ci/blob/releases/2021/4/install_guide_vpu_hddl.md).

> The HDDL plug-in in the container communicates with the daemon on the host, so the daemon must be started before running the container.

## Mixed Device
Based on enabled hardware `MULTI`, `HETERO` and `AUTO` plugins are also supported.
* `MULTI`: The Multi-Device plugin automatically assigns inference requests to available computational devices to execute the requests in parallel. Refer to OpenVINO<sup>&#8482;</sup> [documentation](https://docs.openvino.ai/latest/openvino_docs_IE_DG_supported_plugins_MULTI.html). Example Inference Device `MULTI:CPU,GPU`
* `HETERO`: The heterogeneous plugin enables computing the inference of one network on several devices.Refer to OpenVINO<sup>&#8482;</sup> [documentation](https://docs.openvino.ai/latest/openvino_docs_IE_DG_supported_plugins_HETERO.html). Example Inference Device `HETERO:CPU,GPU`
* `AUTO`: Use `AUTO` as the device name to delegate selection of an actual accelerator to OpenVINO<sup>&#8482;</sup>. Refer to OpenVINO<sup>&#8482;</sup> [documentation](https://docs.openvino.ai/latest/openvino_docs_IE_DG_supported_plugins_AUTO.html). Example Inference Device `AUTO`

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

### Intel(R) DL Streamer based Image in Developer Mode
**Example:**

```bash
docker/run.sh --dev
```
```
pipeline-server@my-host:~$ python3 -m server
```

By default, the running user's UID value determines user name inside the container. A UID of 1001 is assigned as `pipeline-server`. For other UIDs, you may see `I have no name!@my-host`.
To run as another user, you can add `--user <user_name>` to the run command.  i.e. to add pipeline-server by name use add `--user pipeline-server`

---
\* Other names and brands may be claimed as the property of others.
