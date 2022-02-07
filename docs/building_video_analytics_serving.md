# Building Intel(R) DL Streamer Pipeline Server
| [Build Stages](#build-stages) | [Default Build Commands and Image Names](#default-build-commands-and-image-names)  | [Selecting Pipelines and Models at Build Time](#selecting-pipelines-and-models-at-build-time) | [Supported Base Images](#supported-base-images) |

The Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server docker image is designed to be customized
to support different base images, models, pipelines, and application
requirements. The following sections give an overview of the way the
image is built as well as common customization patterns.

> **Note:** Descriptions and instructions below assume a working
> knowledge of docker commands and features. For more information
> see docker [documentation](https://docs.docker.com/get-started/).


# Build Stages
The Pipeline Server docker images are built in stages. Each stage
can be customized to meet an application's requirements.

| Stage | Description |
| ----------- | ----------- |
| **Media Analytics Base Image** |The **Media Analytics Base Image** contains a media framework plus all of its dependencies([GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* or [FFmpeg](https://ffmpeg.org/)* ). |
| **Intel(R) DL Streamer Pipeline Server Library** | Python modules enabling the construction and control of media analytics pipelines. |
| **Models and Pipelines** | Deep learning models in OpenVINO<sup>&#8482;</sup> IR format.  Media analytics pipeline definitions in JSON. |
| **Application / Microservice** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Application or microservice using Intel(R) DL Streamer Pipeline Server python modules to execute media analytics pipelines. By default a Tornado based RESTful microservice is included. |

# Default Build Commands and Image Names

| Command | Media Analytics Base Image | Image Name | Description |
| ---     | ---        | --- | ----        |
| `./docker/build.sh`| **ubuntu20_data_runtime:2021.4.2** docker [image](https://hub.docker.com/r/openvino/ubuntu20_data_runtime) |`dlstreamer-pipeline-server-gstreamer` | Intel(R) DL Streamer based microservice with default pipeline definitions and deep learning models. |
| `./docker/build.sh --framework ffmpeg --open-model-zoo...`| **xeone3-ubuntu1804-analytics-ffmpeg:20.10** docker [image](https://hub.docker.com/r/openvisualcloud/xeon-ubuntu1804-analytics-ffmpeg) |`dlstreamer-pipeline-server-ffmpeg`| FFmpeg Video Analytics based microservice with default pipeline definitions and deep learning models. |
### Building with OpenVINO<sup>&#8482;</sup>, Ubuntu 20.04 and Intel(R) DL Streamer Support
**Example:**
```
./docker/build.sh --framework gstreamer
```

### Building with Ubuntu 18.04, OpenVINO<sup>&#8482;</sup> and FFmpeg Support
**Example:**
```
./docker/build.sh --framework ffmpeg \
  --open-model-zoo-image openvino/ubuntu18_data_dev \
  --open-model-zoo-version 2021.1
```

# Selecting Pipelines and Models at Build Time

By default the Pipeline Server build scripts include a set of sample pipelines and models for object detection, classification, tracking and audio event detection. Developers can select a different set of pipelines and models by specifying their location at build time through the --pipelines and --models flags.

> **Note:** Selected pipeline definitions must match the media
> framework supported in the media analytics base image.

### Specifying Pipelines and Models
> **Note:**  Pipelines(--pipelines) must be within build context.

**Example:**
```bash
./docker/build.sh --framework gstreamer --pipelines /path/to/my-pipelines --models /path/to/my-models
```

The Pipeline Server includes by default the models listed in `models.list.yml` in the models folder. These models are downloaded and converted to IR format during the build using the [model download tool](../tools/model_downloader/README.md).
The above example shows a directory being passed as argument to `--models` option. When its a directory name, the models are expected to be there. You can also pass a yml file as input with a list of models you wish to be included from Open Model Zoo.

**Example:**
```bash
./docker/build.sh --framework gstreamer --pipelines /path/to/my-pipelines --models /path/to/my-models.list.yml
```

# Supported Base Images
All validation is done in docker environment. Host built (aka "bare metal") configurations are not supported. You may customize and rebuild base images from source to meet your runtime requirements.

| **Base Image** | **Framework** | **OpenVINO<sup>&#8482;</sup> Version** | **Link** | **Default** |
|---------------------|---------------|---------------|------------------------|-------------|
| OpenVINO<sup>&#8482;</sup> 2021.4.2 ubuntu20_data_runtime | GStreamer | 2021.4.2 | [Docker Hub](https://hub.docker.com/r/openvino/ubuntu20_data_runtime) | Y |
| Open Visual Cloud 20.10 xeone3-ubuntu1804-analytics-ffmpeg | FFmpeg | 2021.1 | [Docker Hub](https://hub.docker.com/r/openvisualcloud/xeone3-ubuntu1804-analytics-ffmpeg) | Y |

---
\* Other names and brands may be claimed as the property of others.
