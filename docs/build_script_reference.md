# Docker Build Script Reference
The `build.sh` script passes common options to the underlying `docker build` commands for the base and derived images. It enables developers the ability to customize the included components.

Use the --help option to see how the use the script. All arguments are optional.

```
docker/build.sh --help
```
```
usage: build.sh
  [--base base image]
  [--framework ffmpeg || gstreamer]
  [--models path to models directory or model list file or NONE]
  [--open-model-zoo-image specify the OpenVINO<sup>&#8482;</sup> image to be used for downloading models from Open Model Zoo]
  [--open-model-zoo-version specify the version of OpenVINO<sup>&#8482;</sup> image to be used for downloading models from Open Model Zoo]
  [--force-model-download force the download of models from Open Model Zoo]
  [--pipelines path to pipelines directory relative to <source directory of Pipeline Server> or NONE]
  [--base-build-context docker context for building base image]
  [--base-build-dockerfile docker file path used to build base image from build context]
  [--build-option additional docker build option that run in the context of docker build. ex. --no-cache]
  [--base-build-option additional docker build option for docker build of base image]
  [--build-arg additional build args to pass to docker build]
  [--base-build-arg additional build args to pass to docker build for base image]
  [--tag docker image tag]
  [--create-service create an entrypoint to run dlstreamer-pipeline-server as a service]
  [--target build a specific target]
  [--dockerfile-dir specify a different dockerfile directory]
  [--environment-file read and set environment variables from a file. Can be supplied multiple times.]
  [--dry-run print docker commands without running]
```
All command line options are optional. Details of key options and their default values are shown below:
## Base Image (--base)
This is the image that docker builds on. It must contain the full set of framework dependencies needed for either [Intel(R) DL Streamer](https://github.com/openvinotoolkit/dlstreamer_gst) or [FFmpeg Video Analytics](https://github.com/VCDP/FFmpeg-patch) and must match the framework selected with the `--framework` option. If a base image is not defined you must provide the location of the Dockerfile to build the base image (see `--base-build-context` and `--base-build-dockerfile`).

## Framework (--framework)
Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server can use either `gstreamer` or `ffmpeg` for pipeline construction. Select framework with `--framework` option. Default is `gstreamer`.

## Model Directory/File List (--models)
This option can be used to specify path to models directory or a model list file. When its a directory, models used by pipelines are expected to be in this directory. When its a file, the models listed in the file are downloaded and converted to IR format if needed by the [model download tool](../tools/model_downloader/README.md) during build time. If nothing is specified, default models listed in the file `models_list/models.list.yml` are downloaded, converted to IR format if needed and included in the image. If set to `NONE` no models are included and the user must ensure models are made available at runtime by volume mounting.

## Open Model Zoo Image (--open-model-zoo-image)
This option can be used to specify the OpenVINO<sup>&#8482;</sup> base image to be used for downloading models from Open Model Zoo.

For GStreamer, the Pipeline Server build script will automatically choose the Open Model Zoo image as per the table in [section](building_pipeline_server.md#supported-base-images).

For FFmpeg, you **must** specify the Open Model Zoo image to build with (i.e., when using `--framework ffmpeg` provide the image corresponding to the table in [section](building_pipeline_server.md#supported-base-images)).

## Open Model Zoo Version (--open-model-zoo-version)
This option can be used to specify the version of OpenVINO<sup>&#8482;</sup> base image to be used for downloading models from Open Model Zoo.

For GStreamer, the Pipeline Server build script will automatically choose the Open Model Zoo version as per the table in [section](building_pipeline_server.md#supported-base-images).

For FFmpeg, you **must** specify the Open Model Zoo version to build with (i.e., when using `--framework ffmpeg` provide the version corresponding to the table in [section](building_pipeline_server.md#supported-base-images)).

## Force Model Download (--force-model-download)
This option instructs the [model download tool](../tools/model_downloader/README.md) to force download of models from Open Model Zoo using the `models.list.yml` even if they already exist in the models directory. This may be useful to guarantee that the models for your build have been generated using the appropriate version of Open Model Zoo before they are embedded into your freshly built image.

If you have previously built for a different framework, you **must** download these again (or archive your models directory to different name), because the version of Open Model Zoo used by `--framework gstreamer` produces different output than when building with `--framework ffmpeg`.

## Pipeline Directory (--pipelines)
Path to the Pipeline Server pipelines. Path must be within docker build context which defaults to the root of the dlstreamer-pipeline-server project. If not specified, [sample pipelines](../pipelines/gstreamer) are included in the image. If set to `NONE` no pipelines are included and the user must ensure pipelines are made available at runtime by [volume mounting](running_pipeline_server.md#selecting-pipelines-and-models-at-runtime).

## Base Build Context (--base-build-context)
This option is used in conjunction with `--base-build-dockerfile` to specify the docker build file and its context. It must be a git repo URL, path to tarball or path to locally cloned folder.

## Base Build Dockerfile (--base-build-dockerfile)
This option is used in conjunction with `--base-build-context` to specify the docker build file and its context. Default values are framework dependent. If framework is `gstreamer` the dockerfile for `Intel(R) DL Streamer` is selected, otherwise the dockerfile is set for the `FFmpeg Video Analytics` image.

## Build Option (--build-option)
Specify a docker build option when building the Pipeline Server image.

## Base Build Option (--base-build-option)
Specify a docker build option when building the base image.

## Build Arg (--build-arg)
Specify a docker build argument when building the Pipeline Server image.

## Base Build Arg (--base-build-arg)
Specify and docker build argument when building the base image.

## Image Tag (--tag)
Set tag of the Pipeline Server image you build. Default value is `framework` based.
* For `gstreamer` framework: `dlstreamer-pipeline-server-gstreamer`
* For `ffmpeg` framework: `dlstreamer-pipeline-server-ffmpeg`

## Create Service (--create-service)
Build the image as a service. Default value is TRUE.

## Target (--target)
Build a specific target in the Dockerfile.

## Dockerfile Directory (--dockerfile-dir)
Specify a different dockerfile directory.

## Environment File (--environment-file)
Read and set environment variables from a file. Can be supplied multiple times.

## Dry Run (--dry-run)
Print the docker commands without building the image.
