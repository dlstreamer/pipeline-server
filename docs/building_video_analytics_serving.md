# Building Video Analytics Serving
| [Build Stages](#build-stages) | [Default Build Commands and Image Names](#default-build-commands-and-image-names) | [Using Pre-Built Media Analytics Base Images](#using-pre-built-media-analytics-base-images) | [Selecting Pipelines and Models at Build Time](#selecting-pipelines-and-models-at-build-time) | 

The Video Analytics Serving docker image is designed to be customized
to support different base images, models, pipelines, and application
requirements. The following sections give an overview of the way the
image is built as well as common customization patterns.

> **Note:** Descriptions and instructions below assume a working
> knowledge of docker commands and features. For more information
> see docker [documentation](https://docs.docker.com/get-started/).


# Build Stages
Video Analytics Serving docker images are built in stages. Each stage
can be customized to meet an application's requirements.

| Stage | Description |
| ----------- | ----------- |
| **Media Analytics Base Image** |The **Media Analytics Base Image** contains a media framework plus all of its dependencies([GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* or [FFmpeg](https://ffmpeg.org/)* ). <br/><br/>The default `GStreamer`* base image is built using the **DL Streamer** docker [file](https://github.com/opencv/gst-video-analytics/blob/preview/audio-detect/docker/Dockerfile).<br/><br/>The default `FFmpeg`* base image is built using the **FFmpeg Video Analytics** docker [file](https://github.com/VCDP/FFmpeg-patch/blob/ffmpeg4.2_va/docker/Dockerfile.source).<br/><br/> Pre-built base images can also be found in docker hub through the [openvisualcloud](https://hub.docker.com/u/openvisualcloud) and [openvino](https://hub.docker.com/u/openvino) organizations. |
| **Video Analytics Serving Library** | Python modules enabling the construction and control of media analytics pipelines. |
| **Models and Pipelines** | Deep learning models in OpenVINO<sup>&#8482;</sup> IR format.  Media analytics pipeline definitions in JSON. |
| **Application / Microservice** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Application or microservice using Video Analytics Serving python modules to execute media analytics pipelines. By default a Tornado based RESTful microservice is included. |

# Default Build Commands and Image Names

| Command | Media Analytics Base Image | Image Name | Description |
| ---     | ---        | --- | ----        |
| `./docker/build.sh`|**DL Streamer** docker [file](https://github.com/opencv/gst-video-analytics/blob/preview/audio-detect/docker/Dockerfile) |`video-analytics-serving-gstreamer` | DL Streamer based microservice with default pipeline definitions and deep learning models. |
| `./docker/build.sh --framework ffmpeg`| **FFmpeg Video Analytics** docker [file](https://github.com/VCDP/FFmpeg-patch/blob/ffmpeg4.2_va/docker/Dockerfile.source) |`video-analytics-serving-ffmpeg`| FFmpeg Video Analytics based microservice with default pipeline definitions and deep learning models. |         

# Using Pre-Built Media Analytics Base Images

By default Video Analytics Serving builds a base image from the dockerfile for a target media analytics framework. To save time and fulfill specific application requirements, Video Analytics Serving can also be configured to use a pre-built image instead.  

## Building with Open Visual Cloud Base Images

The [Open Visual Cloud](https://01.org/openvisualcloud) project
maintains a set of [docker files](https://01.org/openvisualcloud) and
validated, pre-built images in [docker
hub](https://hub.docker.com/u/openvisualcloud) for both `FFmpeg`*
and `GStreamer`* media analytics.

> **Note:** Open Visual Cloud images with analytics support will contain the supported platform, OS, 
> and the term `analytics` in the name, e.g. `openvisualcloud/xeon-ubuntu1804-analytics-gst`

### Building with XeonE3, Ubuntu 18.0.4 and GStreamer* Support
**Example:**

```bash
./docker/build.sh --framework gstreamer --base openvisualcloud/xeone3-ubuntu1804-analytics-gst
```

### Building with XeonE3, Ubuntu 18.0.4 and FFmpeg* Support
**Example:**

```bash
./docker/build.sh --framework ffmpeg --base openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg 
```

## Building with OpenVINO<sup>&#8482;</sup> Base Images

The [OpenVINO<sup>&#8482;</sup> Toolkit](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit.html) releases a set of validated,
pre-built images in [docker hub](https://hub.docker.com/u/openvinvo)
with `GStreamer`* media analytics support through its **DL
Streamer** component.

> **Note:** OpenVINO base images with DL Streamer support contain `data_dev` in the name, e.g. 
> `openvino/ubuntu18_data_dev` and currently only support GStreamer*

### Building with OpenVINO, Ubuntu 18.0.4 and DL Streamer Support
**Example:**
```
./docker/build.sh --framework gstreamer --base openvino/ubuntu18_data_dev
```

# Selecting Pipelines and Models at Build Time

By default the Video Analytics Serving build scripts include a set of sample pipelines and models for object detection, emotion recognition, and audio event detection. Developers can select a different set of pipelines and models by specifying their location at build time through the `--pipelines` and `--models` flags.

> **Note:** Selected pipeline definitions must match the media
> framework supported in the media analytics base image.


### Specifying Pipelines and Models on top of the Open Visual Cloud Base
**Example:**
```bash
./docker/build.sh --framework gstreamer --base openvisualcloud/xeone3-ubuntu1804-analytics-gst --pipelines /path/to/my-pipelines --models /path/to/my-models 
```


---
\* Other names and brands may be claimed as the property of others.




