## Run Script Reference
Docker images should be run using the `run.sh` script.

Use the --help option to see how the use the script. All arguments are optional.

```
$ docker/run.sh --help
usage: run.sh
  [--framework ffmpeg || gstreamer]
  [--image image]
  [-v additional volume mount to pass to docker run]
  [-e additional environment to pass to docker run]
  [--entrypoint-args additional parameters to pass to entrypoint in docker run]
  [-p additional ports to pass to docker run]
  [--network to pass to docker run]
  [--user to pass to docker run]
  [--name to pass to docker run]
  [--dev run in developer mode]
  [--models path to model directory]
  [--pipelines path to pipelines directory]
```

In the following description, `$source_dir` refers to the root project folder and `$framework` is the selected framework.

### Container modes
The container runs in one of two modes, `service` (default) or `developer`. Service mode configures the environment as follows:
* pipeline and model folder paths are volume mounted if specified
* container has access to the host's GPU (/dev/dri)
* port 8080 is used for service communication

Developer mode is covered in a later section.

### Framework (--framework)
This argument is used as follows:
* to select a default image tag if one is not specified
* to select a default pipelines folder if one is not specified

In `service` mode this argument does __not__ select the framework used at runtime, that is fixed in the image. 

The default value is `gstreamer`.

### Image (--image)
The image filename. If not specified default is name is a follows:
* For `gstreamer` framework: `video-analytics-serving-gstreamer`
* For `ffmpeg` framework: `video-analytics-serving-ffmpeg`

### Pipeline Directory (--pipelines)
Path to pipelines folder. Default values depend on mode:
* for `service` mode default value is path to pipelines included in the image. If a value is specified it is assumed to be a path on the host which is automatically volume mounted.
* for `developer` mode default value is path to pipelines in the local source code ($source_dir/$framework/pipelines). If a different path is specified, the location must be volume mounted using the '-v' option.

### Model Directory (--models)
Similar to `--pipelines` but in developer mode default path is $source_dir/models.

### Developer Mode (--dev)
This argument runs the image in `developer` mode which configures the environment as follows:
* VA Serving source code is supplied by the host
* Framework is defined by the host
* Pipeline and model paths are assumed to be in local source. If not they are specified, host paths must be voluimed mounted.
* /tmp and /dev volumes are mounted from host
* Docker is run in privileged mode
* If entry point is not set, it is set to /bin/bash

### Docker run pass-through options
The following parameters simply map to docker run arguments:
```
  [-v additional volume mount]
  [-e additional environment variables]
  [-p additional ports]
  [--network additional network]
  [--user to pass to docker run]
  [--name to pass to docker run]  
```
