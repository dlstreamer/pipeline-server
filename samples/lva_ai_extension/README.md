# Live Video Analytics AI Extension
## Background
[Live Video Analytics](https://azure.microsoft.com/en-us/services/media-services/live-video-analytics/) (LVA) is a
platform for building AI-based video solutions and applications. It uses a framework with plug-ins (termed [extensions](https://docs.microsoft.com/en-us/azure/media-services/live-video-analytics-edge/media-graph-extension-concept)) for accelerated inferencing. The framework supplies decoded frames to the accelerator and expects inference results in return.

This folder contains sample code for an LVA gRPC AI extension based on VA Serving. The extension has a single pipeline that runs object detection using the [person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/person-vehicle-bike-detection-crossroad-0078) model.

## Prerequisites
Building the container requires a modern Linux distro with the following packages installed:

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Video Analytics Serving requires Docker for it's build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Video Analytics Serving's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](docs/installing_bash_macos.md). |

## Building Container
Run the docker image build script.
```
$ ./docker/build.sh
```
Image name is `video-analytics-serving-lva-ai-extension`

## Running Container
The extension server is a VA Serving application that runs in a docker container.
Use the `run_server.sh` script to start the container. The --help option shows how to use the script. All arguments are optional.
```
$ ./docker/run_server.sh --help
usage: ./run_server.sh
  [ -p : Specify the port to use ] (defaults to 5001)
  [ --pipeline-name : Specify the pipeline name to use ] (defaults to object_detection)
  [ --pipeline-version : Specify the pipeline version to use ] (defaults to person_vehicle_bike_detection)
```
Pipeline name and version can also be set through environment variables PIPELINE_NAME and PIPELINE_VERSION respectively.
> Command line options take precedence over environment variables.

Available pipelines and version combinations:

| Pipeline Name  | Pipeline Version |
| ------------- | ------------- |
| object_detection | person_vehicle_bike_detection  |
| object_classification  | vehicle_attributes_recognition  |
| object_tracking  | person_vehicle_bike_tracking  |

The script also supports all `docker/run.sh` options.

Run with default options as follows
```bash
$ ./docker/run_server.sh
Starting Protocol Server Application
```

Run the following command to monitor the logs from the docker container
```bash
$ docker logs video-analytics-serving-lva-ai-extension_latest -f
```

## Test Client
The test client script `run_client.sh` sends frames(s) to the extension server and prints inference results.
Use the --help option to see how to use the script. All arguments are optional.

```
$ ./docker/run_client.sh --help
usage: ./run_client.sh
  [ --server-ip : Specify the server ip to connect to ] (defaults to 127.0.0.1)
  [ --server-port : Specify the server port to connect to ] (defaults to 5001)
  [ --shared-memory : Enables and uses shared memory between client and server ] (defaults to off)
  [ --sample-file-path : Specify the sample file path to run(file must be inside container or in volume mounted path)] (defaults to samples/lva_ai_extension/sampleframes/sample01.png)
)
```
The script also supports all `docker/run.sh` options.

If you are behind a firewall ensure `no_proxy` contains `127.0.0.1` in docker config and system settings.

Run client with default options as follows
```bash
$ ./docker/run_client.sh
[AIXC] [2020-10-07 14:10:52,269] [MainThread  ] [INFO]: gRPC server address: 127.0.0.1:5001
[AIXC] [2020-10-07 14:10:52,269] [MainThread  ] [INFO]: Sample video frame address: sampleframes/sample01.png
[AIXC] [2020-10-07 14:10:52,269] [MainThread  ] [INFO]: How many times to send sample frame to aix server: 1
[AIXC] [2020-10-07 14:10:52,292] [MainThread  ] [INFO]: Shared memory name: /dev/shm/a5y7aa49
[AIXC] [2020-10-07 14:10:52,297] [MainThread  ] [INFO]: [Received] AckNum: 1
[AIXC] [2020-10-07 14:10:53,376] [MainThread  ] [INFO]: [Received] AckNum: 2
[AIXC] [2020-10-07 14:10:53,377] [MainThread  ] [INFO]: sequence_number: 2
ack_sequence_number: 2
media_sample {
  inferences {
    type: ENTITY
    entity {
      tag {
        value: "person"
        confidence: 0.9980418682098389
      }
      box {
        l: 0.29807692766189575
        t: 0.46875
        w: 0.08413461595773697
        h: 0.3798076808452606
      }
    }
  }
  <snip>
}

[AIXC] [2020-10-07 14:10:53,378] [MainThread  ] [INFO]: Client finished execution
```

## LVA Deployment and Testing
To use the container you just built along with LVA, you can use the deployment manifest template located in deployment folder in conjunction with either the [C#](https://github.com/Azure-Samples/live-video-analytics-iot-edge-csharp) or [Python](https://github.com/Azure-Samples/live-video-analytics-iot-edge-python) samples for LVA on IoT Edge. Make sure to replace the image URI of the lvaExtension module with where you uploaded the container image you just built.

To test the docker container you will need to create a graph topology with gRPC extension and then create a graph instance based on that topology. You can do so using LVA on IoT Edge [C#](https://github.com/Azure-Samples/live-video-analytics-iot-edge-csharp) or [Python](https://github.com/Azure-Samples/live-video-analytics-iot-edge-python) sample code. Use the following JSON for operations.json.

> The manifest and graph topology are based on the [DL Streamer AI extension](https://github.com/Azure/live-video-analytics/tree/milan-dev/utilities/video-analysis/dlstreamer) and have not been tested with this extension, so may need some tweaks.


```JSON
{
    "apiVersion": "1.0",
    "operations": [
        {
            "opName": "GraphTopologySet",
            "opParams": {
                "topologyUrl": "https://raw.githubusercontent.com/Azure/live-video-analytics/master/MediaGraph/topologies/grpcExtension/topology.json"
            }
        },
        {
            "opName": "GraphInstanceSet",
            "opParams": {
                "name": "SampleGraph1",
                "properties": {
                    "topologyName": "InferencingWithGrpcExtension",
                    "description": "Sample graph description",
                    "parameters": [
                        {
                            "name": "rtspUrl",
                            "value": "rtsp://rtspsim:554/media/camera-300s.mkv"
                        },
                        {
                            "name": "rtspUserName",
                            "value": "testuser"
                        },
                        {
                            "name": "rtspPassword",
                            "value": "testpassword"
                        },
                        {
                            "name" : "grpcExtensionAddress",
                            "value" : "tcp://lvaExtension:5001"
                        }
                    ]
                }
            }
        },
        {
            "opName": "GraphInstanceActivate",
            "opParams": {
                "name": "SampleGraph1"
            }
        },
        {
            "opName": "WaitForInput",
            "opParams": {
                "message": "The topology will now be deactivated. Press Enter to continue"
            }
        },
        {
            "opName": "GraphInstanceDeactivate",
            "opParams": {
                "name": "SampleGraph1"
            }
        },
        {
            "opName": "GraphInstanceDelete",
            "opParams": {
                "name": "SampleGraph1"
            }
        },
        {
            "opName": "GraphTopologyDelete",
            "opParams": {
                "name": "InferencingWithGrpcExtension"
            }
        }
    ]
}
```

