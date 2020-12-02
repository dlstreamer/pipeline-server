# Building Video Analytics Serving
| [Build Stages](#build-stages) | [Default Build Commands and Image Names](#default-build-commands-and-image-names) | [Using Pre-Built Media Analytics Base Images](#using-pre-built-media-analytics-base-images) | [Selecting Pipelines and Models at Build Time](#selecting-pipelines-and-models-at-build-time) | [Supported Base Images](#supported-base-images) |

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
| **Media Analytics Base Image** |The **Media Analytics Base Image** contains a media framework plus all of its dependencies([GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* or [FFmpeg](https://ffmpeg.org/)* ). |
| **Video Analytics Serving Library** | Python modules enabling the construction and control of media analytics pipelines. |
| **Models and Pipelines** | Deep learning models in OpenVINO<sup>&#8482;</sup> IR format.  Media analytics pipeline definitions in JSON. |
| **Application / Microservice** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Application or microservice using Video Analytics Serving python modules to execute media analytics pipelines. By default a Tornado based RESTful microservice is included. |

# Default Build Commands and Image Names

| Command | Media Analytics Base Image | Image Name | Description |
| ---     | ---        | --- | ----        |
| `./docker/build.sh`| **ubuntu18_runtime:2021.1** docker [image](https://hub.docker.com/r/openvino/ubuntu18_runtime) |`video-analytics-serving-gstreamer` | DL Streamer based microservice with default pipeline definitions and deep learning models. |
| `./docker/build.sh --framework ffmpeg`| **xeone3-ubuntu1804-analytics-ffmpeg:20.10** docker [image](https://hub.docker.com/r/openvisualcloud/xeon-ubuntu1804-analytics-ffmpeg) |`video-analytics-serving-ffmpeg`| FFmpeg Video Analytics based microservice with default pipeline definitions and deep learning models. |         

# Using Pre-Built Media Analytics Base Images

By default Video Analytics Serving builds using openvino/ubuntu18_runtime:2021.1 base image. Video Analytics Serving can also be configured to use other pre-built image instead. 

> **Note:** Using an image tag is recommended for all base images to ensure that dependencies are locked to a specific version.

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
./docker/build.sh --framework gstreamer --base openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10
```

## Building with OpenVINO<sup>&#8482;</sup> Base Images

The [OpenVINO<sup>&#8482;</sup> Toolkit](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit.html) releases a set of validated,
pre-built images in [docker hub](https://hub.docker.com/u/openvinvo)
with `GStreamer`* media analytics support through its **DL
Streamer** component.

> **Note:** OpenVINO base images with DL Streamer support contain `data_dev` or `runtime` in the name, e.g. 
> `openvino/ubuntu18_data_dev` or `openvino/ubuntu18_runtime` and currently only support GStreamer*. Please refer to [Supported Base Images](#supported-base-images) for a list of tested and compatible base images. 

### Building with OpenVINO, Ubuntu 18.0.4 and DL Streamer Support
**Example:**
```
./docker/build.sh --framework gstreamer --base openvino/ubuntu18_data_dev:2021.1
```
# Selecting Pipelines and Models at Build Time

By default the Video Analytics Serving build scripts include a set of sample pipelines and models for object detection, emotion recognition, and audio event detection. Developers can select a different set of pipelines and models by specifying their location at build time through the `--pipelines` and `--models` flags.

> **Note:** Selected pipeline definitions must match the media
> framework supported in the media analytics base image.


### Specifying Pipelines and Models on top of the Open Visual Cloud Base
**Example:**
```bash
./docker/build.sh --framework gstreamer --base openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10 --pipelines /path/to/my-pipelines --models /path/to/my-models 
```

VA Serving includes by default the models listed in `models.list.yml` in the models folder. These models are downloaded and converted to IR format during the build using the [model download tool](../tools/model_downloader/README.md).  
The above example shows a directory being passed as argument to `--models` option. When its a directory name, the models are expected to be there. You can also pass a yml file as input with a list of models you wish to be included from Open Model Zoo.

**Example:**
```bash
./docker/build.sh --framework gstreamer --base openvisualcloud/xeone3-ubuntu1804-analytics-gst:20.10 --pipelines /path/to/my-pipelines --models /path/to/my-models.list.yml
```

# Supported Base Images
All validation is done in docker environment. Host built configurations are not supported.

| **Base Image** | **Framework** | **Openvino Version** | **Link** | **Default** |
|---------------------|---------------|---------------|------------------------|-------------|
| OpenVINO 2021.1 ubuntu18_runtime | GStreamer | 2021.1 | [Docker Hub](https://hub.docker.com/r/openvino/ubuntu18_runtime) | Y |
| Open Visual Cloud 20.10 xeone3-ubuntu1804-analytics-gst | GStreamer | 2021.1| [Docker Hub](https://hub.docker.com/r/openvisualcloud/xeone3-ubuntu1804-analytics-gst) | N |
| Open Visual Cloud 20.10 xeone3-ubuntu1804-analytics-ffmpeg | FFmpeg | 2021.1 | [Docker Hub](https://hub.docker.com/r/openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg) | Y |

---
\* Other names and brands may be claimed as the property of others.




