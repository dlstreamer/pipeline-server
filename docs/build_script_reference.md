# Docker Build Script Reference
The `build.sh` script passes common options to the underlying `docker build` commands for the base and derived images. It enables developers the ability to customize the included components.

Use the --help option to see how the use the script. All arguments are optional.

```
$ docker/build.sh --help
usage: build.sh
  [--base base image]
  [--framework ffmpeg || gstreamer]
  [--models path to models directory relative to /path/to/video-analytics-serving or NONE]
  [--pipelines path to pipelines directory relative to /path/to/Projects/video-analytics-serving or NONE]
  [--base-build-context docker context for building base image]
  [--base-build-dockerfile docker file used to build base image]
  [--build-option additional docker build option that run in the context of docker build. ex. --no-cache]
  [--base-build-option additional docker build option for docker build of base image]
  [--build-arg additional build args to pass to docker build]
  [--base-build-arg additional build args to pass to docker build for base image]
  [--tag docker image tag]
  [--create-service create an entrypoint to run video-analytics-serving as a service]
  [--target build a specific target]
  [--dockerfile-dir specify a different dockerfile directory]
  [--dry-run print docker commands without running]
```
All command line options are optional. Details of key options and their default values are shown below: 
## Framework (--framework)
VA Serving can use either `gstreamer` or `ffmpeg` for pipeline construction. Select framework with `--framework` option. Default is `gstreamer`.

## Base Image (--base)
This is the image that docker builds on. It must contain the full set of framework dependencies needed for either [DL Streamer](https://github.com/opencv/gst-video-analytics) or [FFmpeg Video Analytics](https://github.com/VCDP/FFmpeg-patch) and must match the framework selected with the `--framework` option. If a base image is not defined you must provide the location of the Dockerfile to build the base image (see `--base-build-context` and `--base-build-dockerfile`).

## Base Build Context (--base-build-context)
This option is used in conjunction with `--base-build-dockerfile` to specify the docker build file and its context. It must be a git repo URL, path to tarball or path to locally cloned folder. 

## Base Build Dockerfile (--base-build-dockerfile)
This option is used in conjunction with `--base-build-context` to specify the docker build file and its context. Default values are framework dependent. If framework is `gstreamer` the dockerfile for `DL Streamer` is selected, otherwise the dockerfile is set for the `FFmpeg Video Analytics` image.

## Pipeline Directory (--pipelines)
Relative path to VA Serving pipelines directory from root of video-analytics-serving project. If not specified, [sample pipelines](../README.md#example-pipelines) are included in the image. If set to `NONE` no pipelines are included and the user must ensure pipelines are made available at runtime by volume mounting.

## Model Directory (--models)
Models used by pipelines are expected to be in this directory. It is a relative path from root of video-analytics-serving project. If not specified, models for sample pipelines are included in the image. If set to `NONE` no models are included and the user must ensure models are made available at runtime by volume mounting.

## Build Arg (--build-arg)
Specify a docker build argument when building the VA Serving image.

## Base Build Arg (--base-build-arg)
Specify and docker build argument when building the base image.

## Image Tag (--tag)
Set tag of VA serving image you build. Default value is `framework` based.
* For `gstreamer` framework: `video-analytics-serving-gstreamer`
* For `ffmpeg` framework: `video-analytics-serving-ffmpeg`
