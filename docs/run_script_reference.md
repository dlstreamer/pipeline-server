## Run Script Reference
The `run.sh` script passes common options to the underlying `docker run` command.

Use the --help option to see how to use the script. All arguments are optional.

```
$ docker/run.sh --help
usage: run.sh
  [--image image]
  [--framework ffmpeg || gstreamer]
  [--models path to models directory]
  [--pipelines path to pipelines directory]
  [-v additional volume mount to pass to docker run]
  [-e additional environment to pass to docker run]
  [--entrypoint-args additional parameters to pass to entrypoint in docker run]
  [-p additional ports to pass to docker run]
  [--network name network to pass to docker run]
  [--user name of user to pass to docker run]
  [--name container name to pass to docker run]
  [--device device to pass to docker run]
  [--dev run in developer mode]
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
The image name. If not specified the default image name is:
* `video-analytics-serving-gstreamer`, for the `gstreamer` framework
* `video-analytics-serving-ffmpeg`, for the `ffmpeg` framework

### Pipeline Directory (--pipelines)
Path to pipelines folder. Default values depend on mode:
* for `service` mode default value is path to pipelines included in the image. If a value is specified it is assumed to be a path on the host which is automatically volume mounted.
* for `developer` mode default value is path to pipelines in the local source code ($source_dir/$framework/pipelines). If a different path is specified, the location must be volume mounted using the '-v' option.

### Model Directory (--models)
Path to models folder. Treated similar to `--pipelines` but in developer mode default path is $source_dir/models.

### Developer Mode (--dev)
This argument runs the image in `developer` mode which configures the environment as follows:

* Starts the container with an interactive bash shell.
* Volume mounts the local source code, models and pipelines
  directories. Any changes made to the local files on the host are
  immediately reflected in the running container. 
* Volume mounts /tmp and /dev paths from the host.
* Uses the docker option `--network=host`. All ports and network interfaces for the host are shared with the container.
* Uses the docker option `--privileged`. Operates the container with elevated privileges.


### Docker run pass-through options
The following parameters simply map to docker run arguments:
```
  [-v additional volume mount]
  [-e additional environment variables]
  [-p additional ports]
  [--network additional network]
  [--user to pass to docker run]
  [--name to pass to docker run]  
  [--device to pass to docker run] 
```
