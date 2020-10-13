# Video Analytics Serving EdgeX Bridge

This sample demonstrates how to emit events into [EdgeX Foundry](http://edgexfoundry.org/) from an object detection pipeline based on Video Analytics Serving and [DL Streamer](https://github.com/openvinotoolkit/dlstreamer_gst). The sample uses the [mobilenet-ssd](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/mobilenet-ssd/mobilenet-ssd.md) model for detection but can be customized to use any detection or recognition model.

| [Overview](#overview) | [Prerequisites](#prerequisites) | [Tutorial](#tutorial) | [Script Arguments](#script-arguments) |

# Overview

## EdgeX Foundry

EdgeX Foundry consists of vendor-neutral open-source middleware that provides a common framework to assemble and deploy solutions that utilize edge-based sensors and interoperates with operational technology and information technology systems. Especially suited for industrial IoT computing, EdgeX consists of a core set of loosely coupled microservices organized in different layers. At the [_South Side_](https://en.wikipedia.org/wiki/EdgeX_Foundry) the framework provides extensive integration of devices and software by use of a number of available device services. Each EdgeX device service is able to support a range of devices so long as they conform to a particular protocol. EdgeX also includes a [device-sdk](https://github.com/edgexfoundry/device-sdk-go/) to create new device services as needed. 

In this sample VA Serving outputs to [MQTT](https://en.wikipedia.org/wiki/MQTT), a popular IoT messaging protocol. These messages are received as [events](https://nexus.edgexfoundry.org/content/sites/docs/snapshots/master/256/docs/_build/html/Ch-WalkthroughReading.html) by a dynamically configured and listening EdgeX deployment.

## Prerequisites

EdgeX requires [Docker Compose](https://docs.docker.com/compose/install/#install-compose-on-linux-systems) to launch its containers. Please install the latest for your platform.

> Note: If you are previously using EdgeX services and have them running on your host, you must stop them before we begin.

## Pipeline

The EdgeX Bridge sample uses a DL Streamer based pipeline definition with a version that desginates its purpose. The reference pipeline `pipelines/object_detect/edgex` uses standard gstreamer elements for parsing, decoding, and converting incoming media files, gvadetect to detect objects in each frame, gvametaconvert to produce json from detections, gvapython to call a custom python module to _transform_ labeled detections, and finally gvametapublish to publish results to the [edgex-device-mqtt](https://github.com/edgexfoundry/device-mqtt-go) device service.

## Object Detection Model

The reference pipeline makes use of an object detection model to detect and label regions of interest. Any objects detected within the region are reported with a label and confidence value, along with location details and other contextually relevant metadata. Multiple objects may be reported in a media frame or image, and behavior may be refined further by assigning a confidence `threshold` property of the [gvadetect](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvadetect) element.

# Tutorial

This self-contained tutorial walks through a working example to fetch and prepare EdgeX configuration to receive Video Analytics Serving object detection events.

### Prepare EdgeX Network and Microservices

1. Fetch the EdgeX developer scripts repository. These contain the [latest EdgeX docker compose files](https://github.com/edgexfoundry/developer-scripts/blob/master/releases/nightly-build/compose-files/source/README.md) we will use to bootstrap our launch of the EdgeX Framework. This script also pulls the base configuration from the device-mqtt container.

   ```
   $ ./samples/edgex_bridge/fetch_edgex.sh
   $ ls ./edgex
     developer-scripts  docker-compose.yml  res
   ```

1. Build and run a developer VA Serving client container. This conveniently volume mounts your video-analytics-serving source folder. In this way, the sample will update the `./edgex` subfolder to inform EdgeX to listen for VA Serving events as they are emitted to the MQTT broker.

   ```
   ./docker/build.sh
   ./docker/run.sh --dev --name vaserving
   ```

1. Within the vaserving container, generate the needed EdgeX resources and augment the configuration found in the `./edgex` subfolder on your host (created in step 1). To do this we will launch the sample edgex_bridge.py script with the `--generate` parameter.

   ```
   vaserving@host:~$ python3 samples/edgex_bridge/edgex_bridge.py --topic object_events --generate
   ```

   Other parameters are available to expand to other pipelines and usages, but their default values are applied for now.

### Launch EdgeX Network and Microservices

1. Now that we have the docker-compose and override configuration for device-mqtt prepared, we are ready to launch the EdgeX platform. In the host terminal session, launch EdgeX platform.

   ```
   $ ./samples/edgex_bridge/start_edgex.sh
   ```

### Confirm EdgeX Device Service and MQTT Device Profile

1. Before proceeding further, check that EdgeX started with the needed setup. Invoke this command and expect a successful HTTP 200 response:

   ```
   curl -i --get http://localhost:48081/api/v1/deviceservice/name/edgex-device-mqtt
   ```

1. Also confirm that when the service loaded it resolved the configuration overrides we generated. To do this, invoke the following command and expect a successful HTTP 200 response:

   ```
   curl -i --get http://localhost:48081/api/v1/device/name/videoAnalytics-mqtt
   ```

### Run VA Serving Pipeline

Return to your terminal running the vaserving session. This time we will process bottle_detection.mp4 to detect objects and send events to EdgeX applications.

NOTE: If you closed the vaserving container simply run the command again (found in step 2 above) and return to follow along here. 

By default the sample processes the file: `video-analytics-serving/samples/bottle_detection.mp4` which contains glass bottles with occasional motion to add and remove a bottle.

   ```bash
   python3 ./samples/edgex_bridge/edgex_bridge.py --topic=objects_detected
   ```

   **Expected Output**:
   ```bash
   {"levelname": "INFO", "asctime": "2020-10-06 19:12:05,847", "message": "Creating Instance of Pipeline object_detection/edgex", "module": "pipeline_manager"}
   {"levelname": "INFO", "asctime": "2020-10-06 19:12:06,323", "message": "Setting Pipeline 1 State to RUNNING", "module": "gstreamer_pipeline"}
   {"levelname": "INFO", "asctime": "2020-10-06 19:12:26,240", "message": "Pipeline 1 Ended", "module": "gstreamer_pipeline"}
   ```

### Confirm EdgeX Received Events

1. Confirm events were received by using your host browser or curl in your host terminal to see results. This reveals the last 100 events received by the default device profile name we configured using `edgex_bridge.py --generate` above.

   ```bash
   curl -i --get http://localhost:48080/api/v1/event/device/videoAnalytics-mqtt/100
   ```

## Modifying for Additional Usages

1. The `edgex_bridge.py` sample allows you to generate and run using other profile names, topics to extend the interactions you may need with your EdgeX applications. Refer to the reference section below for details.

1. The `object_detect/edgex` pipeline is a reference that you can use as a starting point to construct or update other pipelines. Of primary interest will be the gvapython element and parameters which invoke the `extensions/edgex_transform.py` while the pipeline executes.

1. The `extensions/edgex_transform.py` may be modified to inspect detection and tensor values preparing event payloads with tailored data set(s) before they are sent to EdgeX. This is especially useful when processing media or EdgeX application layers on constrained edge devices.

### Deploying Object Detection as an EdgeX Aware Microservice

The created pipeline can be used with the sample Video Analytics Serving microservice.

You may wish to modify the `docker-compose.override.yml` or apply similar techniques to run the VA Serving container whenever EdgeX is started.

1. Update the docker/run.sh command to reflect that `./samples/edgex_bridge/edgex_bridge.py --source=<your media input source>` should run as the container's entrypoint.

1. Rebuild the deployment container

   ```bash
   ./docker/build.sh --base openvisualcloud/xeon-ubuntu1804-analytics-gst
   ```

1. Confirm the container launches as a Microservice

   ```bash
   ./docker/run.sh -e IGNORE_INIT_ERRORS=true -v /tmp:/tmp
   ```

> NOTE: This sample configures a local EdgeX deployment in a simplified form. For production deployment you should refer to EdgeX guides on [running with security components](
https://github.com/edgexfoundry/edgex-go/blob/master/README.md#running-edgex-with-security-components).

## Script Arguments

The `./samples/edgex_bridge/edgex_bridge.py` script accepts the following command line parameters.
 
```
usage: edgex_bridge.py [-h] [--source SOURCE] [--destination DESTINATION]
                       [--edgexdevice EDGEXDEVICE]
                       [--edgexcommand EDGEXCOMMAND]
                       [--edgexresource EDGEXRESOURCE] [--topic TOPIC]
                       [--generate]

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       URI describing the source media to use as input.
                        (default: file:///home/video-analytics-
                        serving/samples/classroom.mp4)
  --destination DESTINATION
                        address of MQTT broker listening for edgex inference
                        results. (default: localhost:1883)
  --edgexdevice EDGEXDEVICE
                        Device name registered with edgex-device-mqtt.
                        (default: videoAnalytics-mqtt)
  --edgexcommand EDGEXCOMMAND
                        EdgeX command declared in the device profile.
                        (default: videoAnalyticsData)
  --edgexresource EDGEXRESOURCE
                        EdgeX device resource declared in the device profile.
                        (default: videoAnalyticsData)
  --topic TOPIC         destination topic associated with EdgeX Core Data
                        (default: objects_detected)
  --generate            Generate EdgeX device profile for device-mqtt.
                        (default: False)
```