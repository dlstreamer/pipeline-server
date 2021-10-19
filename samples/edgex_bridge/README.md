# Video Analytics Serving EdgeX Bridge

This sample demonstrates how to emit events into [EdgeX Foundry](http://edgexfoundry.org/) from an object detection pipeline based on Video Analytics Serving and [DL Streamer](https://github.com/openvinotoolkit/dlstreamer_gst). The sample uses the [person-vehicle-bike-detection-crossroad-0078](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/person-vehicle-bike-detection-crossroad-0078) model for detection but can be customized to use any detection or recognition model.

| [Overview](#overview) | [Prerequisites](#prerequisites) | [Tutorial](#tutorial) | [Script Arguments](#script-arguments) |

# Overview

## EdgeX Foundry

EdgeX Foundry consists of vendor-neutral open-source middleware that provides a common framework to assemble and deploy solutions that utilize edge-based sensors and interoperates with operational technology and information technology systems. Especially suited for industrial IoT computing, EdgeX consists of a core set of loosely coupled microservices organized in different layers. At the [_South Side_](https://en.wikipedia.org/wiki/EdgeX_Foundry) the framework provides extensive integration of devices and software by use of a number of available device services. Each EdgeX device service is able to support a range of devices so long as they conform to a particular protocol. EdgeX also includes a [device-sdk](https://github.com/edgexfoundry/device-sdk-go/) to create new device services as needed.

In this sample VA Serving outputs to [MQTT](https://en.wikipedia.org/wiki/MQTT), a popular IoT messaging protocol. These messages are received as [events](https://nexus.edgexfoundry.org/content/sites/docs/snapshots/master/256/docs/_build/html/Ch-WalkthroughReading.html) by a dynamically configured and listening EdgeX deployment.

## Prerequisites

EdgeX requires [Docker Compose](https://docs.docker.com/compose/install/#install-compose-on-linux-systems) to launch its containers. Please install the latest for your platform.

> Note: If you are previously using EdgeX services and have them running on your host, you must stop them before we begin.

## Pipeline

The EdgeX Bridge sample uses a DL Streamer based pipeline definition with a version that desginates its purpose. The reference pipeline found beneath `./pipelines/object_detect/edgex_event_emitter` uses standard gstreamer elements for parsing, decoding, and converting incoming media files, gvadetect to detect objects within each 15th frame (producing results relative to the source's frame rate), gvametaconvert to produce json from detections, gvapython to call a custom python module to _transform_ labeled detections, and finally gvametapublish to publish results to the [edgex-device-mqtt](https://github.com/edgexfoundry/device-mqtt-go) device service.

## Object Detection Model

The reference pipeline makes use of an object detection model to detect and label regions of interest. Any objects detected within the region are reported with a label and confidence value, along with location details and other contextually relevant metadata. Multiple objects may be reported in a media frame or image, and behavior may be refined further by assigning a confidence `threshold` property of the [gvadetect](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvadetect) element.

The list of objects that this network can detect are:
- person
- vehicle
- bike

# Tutorial

This self-contained tutorial walks through a working example to fetch and prepare EdgeX configuration to receive Video Analytics Serving object detection events.

### Prepare EdgeX Network and Microservices

1. Clone this repository and prepare EdgeX integration:

   ```
   git clone https://github.com/intel/video-analytics-serving.git vasEdge
   cd vasEdge
   ```

1. Run this command to automatically fetch the EdgeX developer scripts repository. These contain the Hanoi release of [EdgeX docker compose files](https://github.com/edgexfoundry/developer-scripts/blob/master/releases/hanoi/compose-files/README.md) we will use to bootstrap our launch of the EdgeX Framework. This script also pulls the base configuration from the device-mqtt container. When it completes you will find a  `./edgex` subfolder is created with these contents.

   ```
   ./samples/edgex_bridge/fetch_edgex.sh
   ls ./samples/edgex_bridge/edgex
   ```
   ```
     developer-scripts  docker-compose.yml  res
   ```

1. Build the sample edgex-video-analytics-serving image.

   ```
   ./samples/edgex_bridge/docker/build.sh
   ```

   This also generates the needed EdgeX resources to augment the `./edgex` project subfolder located on your host (created in step 2). To do this the build script has invoked the [edgex_bridge.py](./edgex_bridge.md) entrypoint, passing in the `--generate` parameter. In this way, the sample will inform EdgeX to listen for VA Serving events as they are emitted to the MQTT broker.

   Other entrypoint parameters are available for your expansion, such as for creating distinctly named microservices with custom pipelines or other usage handling, but their default values are applied for a single microservice to start you off.

### Launch EdgeX Network and Microservices

1. Now that we have the docker-compose and override configuration for device-mqtt prepared, we are ready to launch the EdgeX platform which will now include our built image. In the host terminal session, launch EdgeX platform.
> **Note:**  This sample can only run with Display.
   ```bash
   xhost local:root
   export DISPLAY=<X display you want to render to>
   ./samples/edgex_bridge/start_edgex.sh
   ```

NOTE: The first time this runs, each of the EdgeX microservice images will download to your host. Subsequent runs will make use of these as containers get started.

1. You will find that EdgeX Core Data has received inference events for vehicles detected on frames within the source video input. With this out-of-the-box configuration there are no other events being transmitted to EdgeX, so you can inspect the count of events received using this command:

   ```
   curl -i --get http://localhost:48080/api/v1/event/count
   ```
   ```
   HTTP/1.1 200 OK
   Date: Mon, 29 Mar 2021 03:19:18 GMT
   Content-Length: 3
   Content-Type: text/plain; charset=utf-8

   770
   ```
   With each analysis run we will see another **770** events loading in to EdgeX, each one ready for further processing by EdgeX Rules Engine and Application Services.

1. You are able to explore the event data within EdgeX, by issuing this command. For example, filtering to retrieve three (3) vehicle detection events by the registered `videoAnalytics-mqtt` device:

   ```
   curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/3
   ```
   ```
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Mon, 05 Apr 2021 04:40:42 GMT
   Transfer-Encoding: chunked

   [{"id":"921cc81b-4b64-4f47-9879-8f9c6b3faea3","device":"videoAnalytics-mqtt","created":1617597629183,"origin":1617597629182450826,"readings":[{"id":"7b425176-f1ad-4a3c-8fb2-7386332504ff","created":1617597629183,"origin":1617597629182322723,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.37493348121643066,\"x_min\":0.15006685256958008,\"y_max\":0.9955933094024658,\"y_min\":0.611812949180603},\"confidence\":0.9992963075637817,\"label\":\"vehicle\",\"label_id\":2},\"h\":166,\"roi_type\":\"vehicle\",\"w\":173,\"x\":115,\"y\":264}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":27360000000}","valueType":"String"}]},{"id":"5a56d236-484d-4487-aeab-bff5d6bd5b11","device":"videoAnalytics-mqtt","created":1617597628962,"origin":1617597628962439835,"readings":[{"id":"8de761e4-3bf1-4e3e-bbdf-7b2c2572c83e","created":1617597628962,"origin":1617597628962338556,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.39165395498275757,\"x_min\":0.14272361993789673,\"y_max\":1.0,\"y_min\":0.29326608777046204},\"confidence\":0.9970927238464355,\"label\":\"vehicle\",\"label_id\":2},\"h\":305,\"roi_type\":\"vehicle\",\"w\":191,\"x\":110,\"y\":127}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":26880000000}","valueType":"String"}]},{"id":"396b61e2-4214-4fc6-85c4-da9ff91233b6","device":"videoAnalytics-mqtt","created":1617597628224,"origin":1617597628223052310,"readings":[{"id":"027ab64f-e471-430c-950d-b4ec8092682b","created":1617597628224,"origin":1617597628222903913,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.400143027305603,\"x_min\":0.1788042187690735,\"y_max\":0.7343284487724304,\"y_min\":0.01967310905456543},\"confidence\":0.9986555576324463,\"label\":\"vehicle\",\"label_id\":2},\"h\":309,\"roi_type\":\"vehicle\",\"w\":170,\"x\":137,\"y\":8}],\"resolution\":{\"height\":432,\"width\":768},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":26400000000}","valueType":"String"}]}]
   ```

> Notice these events show what type of object was detected, when it was found, where it was located in the frame, and from what source it originated.

## Extend the Sample

The `edgex-video-analytics-serving` image may be extended by updating sources on your host with the commands we reviewed in the tutorial. You may also choose to update and develop iteratively from within the image itself.

1. The `edgex_bridge.py` sample allows you to generate and run using other profile names, topics to extend the interactions you may need with your EdgeX applications. Refer to the reference section below for details.

1. The `object_detection/edgex_event_emitter` pipeline is a reference that you can use as a starting point to construct or update other pipelines. Of primary interest will be the gvapython element and parameters which invoke the `extensions/edgex_transform.py` while the pipeline executes.

1. The `extensions/edgex_transform.py` may be modified to inspect detection and tensor values preparing event payloads with tailored data set(s) before they are sent to EdgeX. This is especially useful when processing media or EdgeX application layers on constrained edge devices.

1. You may customize the pipeline to use other models.
For example, you may wish to remove the visual output by updating the last line of the pipeline template to replace with the following:

   ```suggestion:-0+0
   -" ! queue ! gvawatermark ! videoconvert ! fpsdisplaysink video-sink=ximagesink"
   +" ! appsink name=appsink"
   ```

   Refer to [Changing Object Detection Models](/docs/changing_object_detection_models.md) for creative guidance.

1. Pass in a new source, representing a camera watching bottles being added or removed, such as "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true"

After you launch build.sh and start_edgex.sh, you will find these events emitted:

   ```
   curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/2
   ```
   ```
   HTTP/1.1 200 OK
   Content-Type: application/json
   Date: Mon, 29 Mar 2021 03:22:11 GMT
   Content-Length: 1652

   [{"id":"373b6f53-6c25-4fd2-8794-a947361286cc","device":"videoAnalytics-mqtt","created":1616987952909,"origin":1616987952909364616,"readings":[{"id":"edfc69ba-860b-45b6-89f0-58fc6a924bc7","created":1616987952909,"origin":1616987952909324668,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9018613696098328,\"x_min\":0.7940059304237366,\"y_max\":0.8923144340515137,\"y_min\":0.3036338984966278},\"confidence\":0.6951693892478943,\"label\":\"bottle\",\"label_id\":5},\"h\":212,\"roi_type\":\"bottle\",\"w\":69,\"x\":508,\"y\":109}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":39821229050}","valueType":"String"}]},{"id":"2864f434-696f-4a86-b3da-c7a96feb9ac0","device":"videoAnalytics-mqtt","created":1616987952909,"origin":1616987952909342261,"readings":[{"id":"4a2aad7f-a26f-4121-b4c9-12fc15774980","created":1616987952909,"origin":1616987952909267268,"device":"videoAnalytics-mqtt","name":"videoAnalyticsData","value":"{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9021463990211487,\"x_min\":0.7939692139625549,\"y_max\":0.8923394680023193,\"y_min\":0.3034985065460205},\"confidence\":0.6987365484237671,\"label\":\"bottle\",\"label_id\":5},\"h\":212,\"roi_type\":\"bottle\",\"w\":69,\"x\":508,\"y\":109}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":39787709497}","valueType":"String"}]}]
   ```


1. Add an application service to consume events and trigger other actions based on insights.

> TIP: You can also monitor the MQTT broker when troubleshooting connectivity by subscribing with a client right on your host.

   ```
   sudo apt-get update && sudo apt-get install mosquitto-clients

   mosquitto_sub -t edgex_bridge/objects_detected
   ```

   This will reveal events received by the EdgeX MQTT Broker as they scroll by.

   ```
   ...
   {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.9158562421798706,\"x_min\":0.7758536338806152,\"y_max\":0.5335087776184082,\"y_min\":0.002240896224975586},\"confidence\":0.5367399454116821,\"label\":\"bottle\",\"label_id\":5},\"h\":191,\"roi_type\":\"bottle\",\"w\":90,\"x\":497,\"y\":1}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":31910614525}"}

   {"name": "videoAnalytics-mqtt", "cmd": "videoAnalyticsData", "method": "get", "videoAnalyticsData": "{\"objects\":[{\"detection\":{\"bounding_box\":{\"x_max\":0.1857132911682129,\"x_min\":0.08316642045974731,\"y_max\":0.9017078876495361,\"y_min\":0.29972949624061584},\"confidence\":0.5077442526817322,\"label\":\"bottle\",\"label_id\":5},\"h\":217,\"roi_type\":\"bottle\",\"w\":66,\"x\":53,\"y\":108}],\"resolution\":{\"height\":360,\"width\":640},\"source\":\"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true\",\"tags\":{},\"timestamp\":33184357542}"}
   ...
   ```

## Troubleshooting

1. When finished remember to stop the EdgeX stack.
   ```
   ./samples/edgex_bridge/stop_edgex.sh
   ```
   ```
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
   Removing edgex-video-analytics-serving        ... done
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

1. To remove all data persisted in EdgeX docker volumes and quickly re-run this exercise from scratch:

   ```
   ./samples/edgex_bridge/clear_edgex.sh

   ./samples/edgex_bridge/docker/build.sh

   ./samples/edgex_bridge/start_edgex.sh
   ```

1. If you are in creative mode and want to more quickly update to try new things, you may directly modify the docker-compose-override.yml to alter `command:` parameters, update `environment:` variables and so on. With new input, Docker compose will automatically launch the container with the new parameters.

   ```
   nano ./samples/edgex_bridge/edgex/docker-compose-override.yml
   ```
   ```
   ...
   image: edgex-video-analytics-serving:0.5.0
   ...
   command: "--source=https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true --topic=vehicles_detected"
   ...
   ```
   ```
   ./samples/edgex_bridge/start_edgex.sh
   ```
   ```
   edgex-core-data is up-to-date
   edgex-core-command is up-to-date
   edgex-app-service-configurable-rules is up-to-date
   edgex-device-mqtt is up-to-date
   edgex-sys-mgmt-agent is up-to-date
   Recreating edgex-video-analytics-serving ...
   Recreating edgex-video-analytics-serving ... done
   ```

> TIP: Use an environment variable to dynamically adjust runtime parameters.
   ```
   ...
       command: $ENTRYPOINT_ARGS
   ...
   ```


### Deploying EdgeX Aware Microservices

You may wish to modify the `docker-compose.override.yml` directly or apply similar techniques to generate and run the VA Serving container whenever EdgeX is started; e.g., when configured with camera sources as input.

> NOTE: This sample configures a local EdgeX deployment in a simplified form. For production deployment you should refer to EdgeX guides on [running with security components](
https://github.com/edgexfoundry/edgex-go/blob/master/README.md#running-edgex-with-security-components).

1. You may choose to deploy many containers with independent responsibilities. For this you will need to build and apply unique container names in the compose YML file, emitting distinct topics as appropriate for your needs.

To independently run edgex-video-analytics-serving in DEV mode, issue this command:

   ```
   ./samples/edgex_bridge/docker/run.sh --dev
   ```
   ```
   vaserving@your-hostname:~$ _

   ```
This provides you with a bash shell with a complete Python runtime development environment so you can update and run within the context of your container. Files updated on your host (source code, models, pipelines, media content, etc.) automatically get reflected in runs of the sample application. This allow you to:

- Modify files using your favorite IDE or editor
- Immediately invoke the container's entrypoint or other commands without needing to rebuild the image.
- Run all changes made on your host within the context of the container
- Run gst-inspect-1.0 and other commands helpful to pipeline development and troubleshooting.

Also note that you may alternately launch independent container(s) on your host (outside of docker compose), using ./samples/edgex_bridge/docker/run.sh.
