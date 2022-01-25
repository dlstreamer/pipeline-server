# Intel(R) DL Streamer Pipeline Server EdgeX Bridge

This sample demonstrates how to emit events into [EdgeX Foundry](http://edgexfoundry.org/) from an object detection pipeline based on Intel(R) DL Streamer Pipeline Server and [Intel(R) DL Streamer](https://github.com/openvinotoolkit/dlstreamer_gst). The sample uses the [person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/person-vehicle-bike-detection-crossroad-0078) model for detection but can be customized to use any detection or recognition model.

| [Overview](#overview) | [Prerequisites](#prerequisites) | [Tutorial](#tutorial) | [Extend Sample](#extend-the-sample) | [Troubleshooting](#troubleshooting) | [Deploying](#deploying-edgex-aware-microservices) | [Script Arguments](./edgex_bridge.md#script-arguments) |

## Overview

This sample is composed of sections that walk you through a step-by-step tutorial and then follows with additional EdgeX integration guidance.

### EdgeX Foundry

EdgeX Foundry consists of vendor-neutral open-source middleware that provides a common framework to assemble and deploy solutions that utilize edge-based sensors and interoperates with operational technology and information technology systems. Especially suited for industrial IoT computing, EdgeX consists of a core set of loosely coupled microservices organized in different layers. At the [_South Side_](https://en.wikipedia.org/wiki/EdgeX_Foundry) the framework provides extensive integration of devices and software by use of a number of available device services. Each EdgeX device service is able to support a range of devices so long as they conform to a particular protocol. EdgeX also includes a [device-sdk](https://github.com/edgexfoundry/device-sdk-go/) to create new device services as needed.

In this sample VA Serving outputs to [MQTT](https://en.wikipedia.org/wiki/MQTT), a popular IoT messaging protocol. These messages are received as [events](https://nexus.edgexfoundry.org/content/sites/docs/snapshots/master/256/docs/_build/html/Ch-WalkthroughReading.html) by a dynamically configured and listening EdgeX deployment.

### Prerequisites

This section lists additional dependencies needed to complete this tutorial, beyond the [primary VA Serving prerequisites](/README.md#prerequisites).

* EdgeX requires [Docker Compose](https://docs.docker.com/compose/install/#install-compose-on-linux-systems) to launch its containers. Please install the latest for your platform.

> Note: If you are previously using EdgeX services and have them running on your host, you must stop them before we begin.

* \[optional\] To optionally view rendered pipelines and detections, we will rely on an installed RTSP client (e.g., [VLC Media Player*](https://linuxize.com/post/how-to-install-vlc-on-ubuntu-20-04/) or [FFplay*](https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-20-04/)).

### Pipeline

The EdgeX Bridge sample uses a Intel(R) DL Streamer based pipeline definition with a version that designates its purpose. The reference pipeline found beneath `./pipelines/object_detect/edgex_event_emitter` uses standard gstreamer elements for parsing, decoding, and converting incoming media files, gvadetect to detect objects within each 15th frame (producing results relative to the source's frame rate), gvametaconvert to produce json from detections, gvapython to call a custom python module to _transform_ labeled detections, and finally gvametapublish to publish results to the [edgex-device-mqtt](https://github.com/edgexfoundry/device-mqtt-go) device service.

### Object Detection Model

The reference pipeline makes use of an object detection model to detect and label regions of interest. Any objects detected within the region are reported with a label and confidence value, along with location details and other contextually relevant metadata. Multiple objects may be reported in a media frame or image, and behavior may be refined further by assigning a confidence `threshold` property of the [gvadetect](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvadetect) element.

The list of objects that this network can detect are:

- person
- vehicle
- bike

## Tutorial

This self-contained tutorial walks through a working example to fetch and prepare EdgeX configuration to receive Intel(R) DL Streamer Pipeline Server object detection events. Confirm prerequisites are installed before we begin.

   ```bash
   docker-compose --version
   ```

   Should show a version similar to this:

   ```code
   docker-compose version 1.27.4, build 40524192
   ```

### Prepare EdgeX Network and Microservices

1. Clone this repository to a distinct location on your host:

   ```bash
   cd ~/dev
   git clone https://github.com/intel/dlstreamer-pipeline-server.git vasEdge
   cd vasEdge/samples/edgex_bridge
   ```

1. Fetch the EdgeX developer scripts repository:

   ```bash
   ./fetch_edgex.sh
   ls ./edgex
   ```

   Should show contents similar to this:

   ```code
     developer-scripts  docker-compose.yml  res
   ```

   > NOTE: This fetches the EdgeX `Hanoi` release of [EdgeX docker compose files](https://github.com/edgexfoundry/developer-scripts/blob/master/releases/hanoi/compose-files/README.md) that we will use to bootstrap our launch of the EdgeX Framework. This script also pulls the base configuration from the device-mqtt container. When it completes you will find a  `./edgex` subfolder is created with these contents.

1. Build the sample `dlstreamer-pipeline-server-edgex` image:

   ```bash
   ./docker/build.sh
   ```

   > NOTE: This also generates the needed EdgeX resources to augment the `./edgex` project subfolder located on your host (created in step 2). To do this the build script has invoked the [edgex_bridge.py](./edgex_bridge.md) entrypoint, passing in the `--generate` parameter. In this way, the sample will inform EdgeX to listen for VA Serving events as they are emitted to the MQTT broker.

   Default values are applied for a single microservice to start you off with entrypoint parameters available for your expansion. You may expand on this example later by creating distinctly named microservices that each run a custom pipeline, or opt to dynamically handle other conditional workloads and use cases.

### Launch EdgeX Network and Microservices

1. Now that we have the docker-compose and override configuration for device-mqtt prepared, we are ready to launch the EdgeX platform which will now include our built image. In the host terminal session, launch EdgeX platform.

   ```bash
   ./start_edgex.sh
   ```

   > NOTE: The first time this runs, each of the EdgeX microservice Docker images will automatically download to your host. The `edgex-dlstreamer-pipeline-server` container will launch after the `edgex-device-mqtt` container reports it is healthy.

#### Inspect Results and EdgeX References

1. You will find that EdgeX Core Data has received inference events for vehicles detected on frames within the source video input. With this out-of-the-box configuration there are no other events being transmitted to EdgeX, so you can inspect the count of events received using this command:

   ```bash
   ./check_event_count.sh
   ```

   Should reveal the count of events received by EdgeX Core Data:

   ```shell
   HTTP/1.1 200 OK
   Date: Fri, 31 Dec 2021 00:00:00 GMT
   Content-Length: 3
   Content-Type: text/plain; charset=utf-8

   22
   ```

   With each analysis run we will see another **22** events loading in to EdgeX, each one ready for further processing by EdgeX Rules Engine and Application Services. You may easily trigger these by re-running `./start_edgex.sh` since the edgex-dlstreamer-pipeline-server container exits after it completes processing of the .mp4/stream.

   > HINT: If you do get event count 0, check the [troubleshooting](#troubleshooting) section to inspect logs.

1. You are able to explore the event data within EdgeX, by issuing this command. For example, filtering to retrieve three (3) vehicle detection events by the registered `videoAnalytics-mqtt` device:

   ```bash
   curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/3
   ```

   Example Response:

   ```shell
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Fri, 31 Dec 2021 00:00:00 GMT
   Transfer-Encoding: chunked

   [{"id":"921cc81b-4b64-4f47-9879-8f9c6b3faea3","device":"videoAnalytics-mqtt","created":1617597629183,"origin":1617597629182450826,"readings":[{"id":"7b425176-f1ad-4a3c-8fb2-7386332504ff","created":1617597629183,"origin":1617597629182322723,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.37493348121643066,\"x_min\":0.15006685256958008,\"y_max\":0.9955933094024658,\"y_min\":0.611812949180603},\"confidence\":0.9992963075637817,\"label\":\"vehicle\",\"label_id\":2},\"h\":166,\"roi_type\":\"vehicle\",\"w\":173,\"x\":115,\"y\":264}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":27360000000}","valueType":"String"}]},{"id":"5a56d236-484d-4487-aeab-bff5d6bd5b11","device":"videoAnalytics-mqtt","created":1617597628962,"origin":1617597628962439835,"readings":[{"id":"8de761e4-3bf1-4e3e-bbdf-7b2c2572c83e","created":1617597628962,"origin":1617597628962338556,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.39165395498275757,\"x_min\":0.14272361993789673,\"y_max\":1.0,\"y_min\":0.29326608777046204},\"confidence\":0.9970927238464355,\"label\":\"vehicle\",\"label_id\":2},\"h\":305,\"roi_type\":\"vehicle\",\"w\":191,\"x\":110,\"y\":127}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":26880000000}","valueType":"String"}]},{"id":"396b61e2-4214-4fc6-85c4-da9ff91233b6","device":"videoAnalytics-mqtt","created":1617597628224,"origin":1617597628223052310,"readings":[{"id":"027ab64f-e471-430c-950d-b4ec8092682b","created":1617597628224,"origin":1617597628222903913,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.400143027305603,\"x_min\":0.1788042187690735,\"y_max\":0.7343284487724304,\"y_min\":0.01967310905456543},\"confidence\":0.9986555576324463,\"label\":\"vehicle\",\"label_id\":2},\"h\":309,\"roi_type\":\"vehicle\",\"w\":170,\"x\":137,\"y\":8}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":26400000000}","valueType":"String"}]}]
   ```

   > Notice these events show what type of object was detected, when it was found, where it was located in the frame, and from what source it originated.

   > HINT: If you don't see immediate results, check for an error:

   ```bash
   docker logs edgex-dlstreamer-pipeline-server
   ```

#### Render Pipeline Output

Viewing your input stream is a critical calibration and troubleshooting step.

![rendered pipeline](/samples/edgex_bridge/docs/edgex_pipeline_rendering.gif?raw=true)

To do this let's install an RTSP client such as [VLC Media Player*](https://linuxize.com/post/how-to-install-vlc-on-ubuntu-20-04/) or [FFplay*](https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-20-04/).

You may extend this script or directly use any other client to connect with the RTSP endpoint being served at `rtsp://127.0.0.1:8554/edgex_event_emitter`.

Refer to our [RTSP Re-streaming](/docs/running_video_analytics_serving.md#real-time-streaming-protocol-rtsp-re-streaming) documentation for additional details.

> NOTE: This has been tested when running the RTSP client on the local host. Additional configuration may be needed to view when accessing remotely, bearing in mind that docker-compose is running containers within edgex_network.

**VLC**:

```bash
sudo apt update && sudo apt install vlc
```

With this rendering client in place, launch using:

```bash
./start_edgex.sh --rtsp-client vlc
```

**ffplay**:

```bash
sudo apt update && apt install ffmpeg
```

With this rendering client in place, launch using:

```bash
./start_edgex.sh --rtsp-client ffplay
```

**Manually Connect RTSP Client**:

```bash
./start_edgex.sh --rtsp-path vehicle_detection
```

## Extend the Sample

The `dlstreamer-pipeline-server-edgex` image may be extended by updating sources on your host with the commands we reviewed in the tutorial. You may also choose to update and develop iteratively from within the image itself.

### Creative Mode

1. You may customize the sample pipeline to use other models or perform other runtime behaviors.

   Refer to [Changing Object Detection Models](/docs/changing_object_detection_models.md) for creative guidance.

   > NOTE: Each time you make changes to the pipeline definition you will need to run `./docker/build.sh` so the update is reflected in the `dlstreamer-pipeline-server-edgex` image. If you prefer to make many _iterative_ changes, an alternative to this is to volume mount your local folder and instruct our container to use what currently persists on your host's pipeline.json.

   To mount to the pipelines folder on your host, allowing direct pipeline.json changes to take effect inside your container, uncomment the line in ./edgex/docker.compose.override`:

   ```suggestion:-0+0
   <snip>
   #      - ./../pipelines:/home/pipeline-server/samples/edgex_bridge/pipelines
   ```

1. The `edgex_bridge.py` sample allows you to generate and run using other profile names, topics to extend the interactions you may need with your EdgeX applications. Refer to the reference section below for details.

1. The `object_detection/edgex_event_emitter` pipeline is a reference that you can use as a starting point to construct or update other pipelines. Of primary interest will be the gvapython element and parameters which invoke the `extensions/edgex_transform.py` while the pipeline executes.

1. The `extensions/edgex_transform.py` may be modified to inspect detection and tensor values preparing event payloads with tailored data set(s) before they are sent to EdgeX. This is especially useful when processing media or EdgeX application layers on constrained edge devices.

1. Change to a [mobilenet-ssd](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/mobilenet-ssd/model.yml) model and pass in a new source, representing a camera watching bottles being added or removed, such as "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true"

   After you launch ./docker/build.sh and start_edgex.sh, you will find these events emitted:

   ```bash
   curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/2
   ```

   ```shell
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Fri, 31 Dec 2021 00:00:00 GMT
   Content-Length: 1652

   [{"id":"373b6f53-6c25-4fd2-8794-a947361286cc","device":"videoAnalytics-mqtt","created":1616987952909,"origin":1616987952909364616,"readings":[{"id":"edfc69ba-860b-45b6-89f0-58fc6a924bc7","created":1616987952909,"origin":1616987952909324668,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9018613696098328,\"x_min\":0.7940059304237366,\"y_max\":0.8923144340515137,\"y_min\":0.3036338984966278},\"confidence\":0.6951693892478943,\"label\":\"bottle\",\"label_id\":5},\"h\":212,\"roi_type\":\"bottle\",\"w\":69,\"x\":508,\"y\":109}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":39821229050}","valueType":"String"}]},{"id":"2864f434-696f-4a86-b3da-c7a96feb9ac0","device":"videoAnalytics-mqtt","created":1616987952909,"origin":1616987952909342261,"readings":[{"id":"4a2aad7f-a26f-4121-b4c9-12fc15774980","created":1616987952909,"origin":1616987952909267268,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9021463990211487,\"x_min\":0.7939692139625549,\"y_max\":0.8923394680023193,\"y_min\":0.3034985065460205},\"confidence\":0.6987365484237671,\"label\":\"bottle\",\"label_id\":5},\"h\":212,\"roi_type\":\"bottle\",\"w\":69,\"x\":508,\"y\":109}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":39787709497}","valueType":"String"}]}]
   ```

1. Add an application service to consume events and trigger other actions based on insights.

   > TIP: You can also monitor the MQTT broker when troubleshooting connectivity by subscribing with a client right on your host.

   ```bash
   sudo apt-get update && sudo apt-get install mosquitto-clients

   mosquitto_sub -t edgex_bridge/objects_detected
   ```

   This will reveal events received by the EdgeX MQTT Broker as they scroll by.

   ```bash
   ...
   {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9158562421798706,\"x_min\":0.7758536338806152,\"y_max\":0.5335087776184082,\"y_min\":0.002240896224975586},\"confidence\":0.5367399454116821,\"label\":\"bottle\",\"label_id\":5},\"h\":191,\"roi_type\":\"bottle\",\"w\":90,\"x\":497,\"y\":1}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":31910614525}"}

   {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.1857132911682129,\"x_min\":0.08316642045974731,\"y_max\":0.9017078876495361,\"y_min\":0.29972949624061584},\"confidence\":0.5077442526817322,\"label\":\"bottle\",\"label_id\":5},\"h\":217,\"roi_type\":\"bottle\",\"w\":66,\"x\":53,\"y\":108}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":33184357542}"}
   ...
   ```

#### Runtime Modifications

1. If you are in creative mode and want to more quickly update to try new things, you may directly modify the docker-compose-override.yml to alter `command:` parameters, update `environment:` variables and so on. With new input, Docker compose will automatically launch the container with the new parameters.

   Use vim (or your favorite text editor):

   ```bash
   vim ./samples/edgex_bridge/edgex/docker-compose-override.yml
   ```

   Update the values beneath our image declaration. For example to change the source input, modify the `command:` entry:

   ```suggestion:-0+0
   ...
   image: dlstreamer-pipeline-server-edgex:latest
   ...
   command: "--source=https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true --topic=vehicles_detected"
   ...
   ```

   Launch the sample again:

   ```bash
   ./start_edgex.sh
   ```

   ```code
   edgex-core-data is up-to-date
   edgex-core-command is up-to-date
   edgex-app-service-configurable-rules is up-to-date
   edgex-device-mqtt is up-to-date
   edgex-sys-mgmt-agent is up-to-date
   Recreating edgex-dlstreamer-pipeline-server ...
   Recreating edgex-dlstreamer-pipeline-server ... done
   ```

   > TIP: You can optionally control the full set of commands by using an environment variable. This will allow more complete dynamic adjustment of runtime parameters.

   ```bash
   ...
       command: $ENTRYPOINT_ARGS
   ...
   ```

#### Stopping and Cleanup

1. When finished remember to stop the EdgeX stack.

   ```bash
   ./stop_edgex.sh
   ```

   ```console
   /vasEdge/samples/edgex_bridge$ ./stop_edgex.sh
   Stopping edgex-kuiper                         ... done
   Stopping edgex-app-service-configurable-rules ... done
   Stopping edgex-sys-mgmt-agent                 ... done
   Stopping edgex-device-mqtt                    ... done
   Stopping edgex-core-data                      ... done
   Stopping edgex-core-command                   ... done
   Stopping edgex-core-metadata                  ... done
   Stopping edgex-support-notifications          ... done
   Stopping edgex-support-scheduler              ... done
   Stopping edgex-redis                          ... done
   Stopping edgex-core-consul                    ... done
   Stopping edgex-mqtt-broker                    ... done
   Removing edgex-kuiper                         ... done
   Removing edgex-dlstreamer-pipeline-server        ... done
   Removing edgex-app-service-configurable-rules ... done
   Removing edgex-sys-mgmt-agent                 ... done
   Removing edgex-device-mqtt                    ... done
   Removing edgex-core-data                      ... done
   Removing edgex-core-command                   ... done
   Removing edgex-core-metadata                  ... done
   Removing edgex-support-notifications          ... done
   Removing edgex-support-scheduler              ... done
   Removing edgex-redis                          ... done
   Removing edgex-core-consul                    ... done
   Removing edgex-mqtt-broker                    ... done
   Removing network edgex_edgex-network
   NOTE: EdgeX data still persists in docker volumes.
   ```

1. To remove all data persisted in EdgeX docker volumes and re-register services and resources with EdgeX from scratch, this command will stop all services and remove volumes:

   ```bash
   ./clear_edgex.sh

   ./docker/build.sh

   ./start_edgex.sh
   ```

## Troubleshooting

1. You may wish to modify the `docker-compose.override.yml` directly or apply similar techniques to generate and run the VA Serving container whenever EdgeX is started; e.g., modifying command string to configure with different camera sources as input.

   For example, if you encounter permission issues consider assigning `user` in the docker-compose.override.yml but keep in mind that it will be re-generated when you next run ./docker/build.sh. Update `edgex_bridge.py` if you want to make your changes permanent.

1. Alternately, with the rest of EdgeX stack running you may attempt to run the container separately. Notice we must override the address of edgex-device-mqtt with localhost since we are on host network. For this reason the run.sh script will override the entrypoint destination parameter for edgex-device-mqtt to use 'localhost'.

   ```bash
   ./docker/run.sh
   ```

1. Check logs by issuing:

   ```bash
   docker logs edgex-dlstreamer-pipeline-server
   ```

1. Manually inspect contents of the container by running this command:

   ```bash
   docker run -it --entrypoint /bin/bash edgex-dlstreamer-pipeline-server
   ```

1. To independently run edgex-dlstreamer-pipeline-server in DEV mode, issue this command:

   ```bash
   ./docker/run.sh --dev --user $UID:$GID
   ```

   You will then be running within the bash shell of your container:

   ```console
   pipeline-server@your-hostname:~$ _
   ```

   This provides you with a bash shell with a complete Python runtime development environment so you can update and run within the context of your
   container. Files updated on your host (source code, models, pipelines, media content, etc.) beneath the vasEdge folder (created in step 1) automatically get reflected in runs of the sample application. This allow you to:

   - Modify files using your favorite IDE or editor
   - Immediately invoke the container's entrypoint or other commands without needing to rebuild the image.
   - Run all changes made on your host within the context of the container
   - Run gst-inspect-1.0 and other commands helpful to pipeline development and troubleshooting.

   Also note that you may alternately launch independent container(s) on your host (outside of docker compose), using `./docker/run.sh`.

### EdgeX References

You will see the following results by probing EdgeX endpoints. These are useful for your integration with EdgeX Application Services.

1. Remember this sample shows that the `edgex-dlstreamer-pipeline-server` container is forwarding detection events through the `edgex-device-mqtt` device service which is registered with EdgeX and we can view details reported by edgex-core-metadata (which responds on port 48081):

   ```bash
   curl -i --get http://localhost:48081/api/v1/deviceservice/name/edgex-device-mqtt
   ```

   ```shell
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Fri, 31 Dec 2021 00:00:00 GMT
   Content-Length: 556

   {"created":1618541037387,"modified":1632509089030,"origin":1632509089024,"id":"e80546ec-3d9c-4c82-b35a-e5cece584b0d","name":"edgex-device-mqtt","operatingState":"ENABLED","addressable":{"created":1618541037386,"modified":1632509089024,"origin":1618541037384,"id":"e5635f0b-de7a-44aa-856f-58098cf66bce","name":"edgex-device-mqtt","protocol":"HTTP","method":"POST","address":"edgex-device-mqtt","port":49982,"path":"/api/v1/callback","baseURL":"http://edgex-device-mqtt:49982","url":"http://edgex-device-mqtt:49982/api/v1/callback"},"adminState":"UNLOCKED"}
   ```

1. Confirm our designated device profile is registered with EdgeX:

   ```bash
   curl -i --get http://localhost:48081/api/v1/device/name/videoAnalytics-mqtt
   ```

   ```shell
   {
      "created": 1638752473489,
      "modified": 1638752473489,
      "origin": 1638752473485,
      "description": "MQTT device that receives media analytics events.",
      "id": "c4889695-0ba5-4482-829e-ce008365a439",
      "name": "videoAnalytics-mqtt",
      "adminState": "UNLOCKED",
      "operatingState": "ENABLED",
      "protocols": {
         "mqtt": {
            "ClientId": "videoAnalytics-pub",
            "Host": "localhost",
            "Password": "",
            "Port": "1883",
            "Schema": "tcp",
            "Topic": "videoAnalyticsTopic",
            "User": ""
         }
      },
      "labels": ["MQTT", "VideoAnalyticsServing"],
      "service": {
         "created": 1638752473466,
         "modified": 1638752473466,
         "origin": 1638752473463,
         "id": "17137317-b718-4032-a85d-f0c5a4b521b8",
         "name": "edgex-device-mqtt",
         "operatingState": "ENABLED",
         "addressable": {
            "created": 1638752473462,
            "modified": 1638752473462,
            "origin": 1638752473456,
            "id": "857e4fb1-5760-4421-95a0-0ff5b26a9caf",
            "name": "edgex-device-mqtt",
            "protocol": "HTTP",
            "method": "POST",
            "address": "edgex-device-mqtt",
            "port": 49982,
            "path": "/api/v1/callback",
            "baseURL": "http://edgex-device-mqtt:49982",
            "url": "http://edgex-device-mqtt:49982/api/v1/callback"
         },
         "adminState": "UNLOCKED"
      },
      "profile": {
         "created": 1638752473481,
         "modified": 1638752473481,
         "description": "Device profile for inference events published by Intel(R) DL Streamer Pipeline Server over MQTT.",
         "id": "bbf57a53-be3c-4e0b-800e-d3a1257bb567",
         "name": "videoAnalytics-mqtt",
         "manufacturer": "VideoAnalyticsServing",
         "model": "MQTT-2",
         "labels": ["MQTT", "VideoAnalyticsServing"],
         "deviceResources": [{
            "description": "Inference with one or more detections on an analyzed media frame.",
            "name": "videoAnalyticsData",
            "properties": {
               "value": {
                  "type": "String",
                  "readWrite": "R"
               },
               "units": {
                  "type": "String",
                  "readWrite": "R"
               }
            }
         }],
         "deviceCommands": [{
            "name": "videoAnalyticsData",
            "get": [{
               "operation": "get",
               "object": "videoAnalyticsData",
               "deviceResource": "videoAnalyticsData",
               "parameter": "videoAnalyticsData"
            }]
         }]
      }
   }
   ```

1. Confirm our device command is known by the EdgeX Core Command microservice:

   ```bash
   curl -i --get http://edgex-core-command:48082/api/v1/device
   ```

   ```shell
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Fri, 31 Dec 2021 00:00:00 GMT
   Content-Length: 170
   [
      {
         "id": "de0f3609-baeb-492c-a5bf-12ee58c75b2e",
         "name": "videoAnalytics-mqtt",
         "adminState": "UNLOCKED",
         "operatingState": "ENABLED",
         "labels": [
               "MQTT",
               "VideoAnalyticsServing"
         ]
      }
   ]
   ```

#### EdgeX Event Details

In addition to event counts, we can probe for incoming event details by querying EdgeX Core Data (listening on port 48080). These can be configured in EdgeX to persist or disappear upon handling; e.g., after they are processed by EdgeX Rules Engine or EdgeX Application Services.

```bash
curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/100
```

```shell
HTTP/1.1 200 OK
Content-Type: application/json
Date: Fri, 31 Dec 2021 00:00:00 GMT
Transfer-Encoding: chunked
[{
  "id": "0470f72d-25be-4437-8598-1d80c31a01e7",
  "device": "videoAnalytics-mqtt",
  "created": 1638759383162,
  "origin": 1638759383162549862,
  "readings": [{
    "id": "c41bc60d-941f-4396-903d-216b328fa693",
    "created": 1638759383162,
    "origin": 1638759383162498797,
    "device": "videoAnalytics-mqtt",
    "name": "videoAnalyticsData",
    "value": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.3749333620071411,\"x_min\":0.15006709098815918,\"y_max\":0.9955933094024658,\"y_min\":0.611812949180603},\"confidence\":0.9992963075637817,\"label\":\"vehicle\",\"label_id\":2},\"h\":166,\"roi_type\":\"vehicle\",\"w\":173,\"x\":115,\"y\":264}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":27360000000}",
    "valueType": "String"
  }]
},
<snip>
{
  "id": "b1c9f516-c0c6-4c1f-bf66-dcfb6be09ec4",
  "device": "videoAnalytics-mqtt",
  "created": 1638759381056,
  "origin": 1638759381055267583,
  "readings": [{
    "id": "0f07fb5f-281f-44fd-9fd4-69607943c752",
    "created": 1638759381056,
    "origin": 1638759381055194798,
    "device": "videoAnalytics-mqtt",
    "name": "videoAnalyticsData",
    "value": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.633696436882019,\"x_min\":0.3582877814769745,\"y_max\":1.0,\"y_min\":0.7601467967033386},\"confidence\":0.5017350316047668,\"label\":\"vehicle\",\"label_id\":2},\"h\":104,\"roi_type\":\"vehicle\",\"w\":212,\"x\":275,\"y\":328}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":4800000000}",
    "valueType": "String"
  }]
}
```

> NOTE: These have a limited lifetime by default. As you will see if you check `edgex-core-data` logs.

```bash
docker logs edgex-core-data
```

```bash
<snip>
level=INFO app=edgex-core-data source=router.go:567 msg="Deleting events by age: 604800000"
level=INFO app=edgex-core-data source=event.go:349 msg="Scrubbing events.  Deleting all events that have been pushed"
```

#### EdgeX Commands

The EdgeX videoAnalyticsData command receives the VA Serving events. These will hold values of detections/classifications that otherwise match standard VA Serving pipeline results. Examples:

- Vehicles detected by `person-vehicle-bike-detection-crossroad-0078` currently defined in `./models_list/models.list.yml`

  ```bash
  {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.39165401458740234,\"x_min\":0.1427236944437027,\"y_max\":1.0,\"y_min\":0.2932662069797516},\"confidence\":0.9970927238464355,\"label\":\"vehicle\",\"label_id\":2},\"h\":305,\"roi_type\":\"vehicle\",\"w\":191,\"x\":110,\"y\":127}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":26880000000}"}
  ```

- Bottles detected by mobilenet-ssd:

  ```bash
  {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9158562421798706,\"x_min\":0.7758536338806152,\"y_max\":0.5335087776184082,\"y_min\":0.002240896224975586},\"confidence\":0.5367399454116821,\"label\":\"bottle\",\"label_id\":5},\"h\":191,\"roi_type\":\"bottle\",\"w\":90,\"x\":497,\"y\":1}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":31910614525}"}
  ```

## Deploying EdgeX Aware Microservices

> NOTE: This sample configures a local EdgeX deployment in a simplified form. For production deployment you should refer to EdgeX guides on [running with security components](
https://github.com/edgexfoundry/edgex-go/blob/master/README.md#running-edgex-with-security-components).

1. You may choose to deploy many containers with independent responsibilities. For this you will need to build and apply unique container names in the compose YML file, emitting distinct topics as appropriate for your needs.

2. Modify the fetch_edgex.sh to construct Docker compose file using security best practices, the boilerplate compose file should use a read only file system.

3. Understand and apply the production security requirements appropriate to your container's runtime environment and your production use case.
