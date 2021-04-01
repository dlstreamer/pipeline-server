# Video Analytics Serving
| [Getting Started](#getting-started) | [Documentation](#further-reading) | [Reference Guides](#further-reading) | [Related Links](#related-links) | [Known Issues](#known-issues) |

Video Analytics Serving is a python package and microservice for
deploying optimized media analytics pipelines. It supports pipelines
defined in
[GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)*
or [FFmpeg](https://ffmpeg.org/)* and provides APIs to discover, start,
stop, customize and monitor pipeline execution. Video Analytics
Serving is based on [OpenVINO<sup>&#8482;</sup> Toolkit DL
Streamer](https://github.com/opencv/gst-video-analytics) and [FFmpeg
Video Analytics](https://github.com/VCDP/FFmpeg-patch).

## Features Include:
| |                  |
|---------------------------------------------|------------------|
| **Customizable Media Analytics Containers** | Scripts and dockerfiles to build and run container images with the required dependencies for hardware optimized media analytics pipelines. |
| **No-Code Pipeline Definitions and Templates** | JSON based definition files, a flexible way for developers to define and parameterize pipelines while abstracting the low level details from their users. |
| **Deep Learning Model Integration** | A simple way to package and reference [OpenVINO<sup>&#8482;</sup>](https://software.intel.com/en-us/openvino-toolkit) based models in pipeline definitions. The precision of a model can be auto-selected at runtime based on the chosen inference device. |
| **Video Analytics Serving Python API** | A python module to discover, start, stop, customize and monitor pipelines based on their no-code definitions. |
| **Video Analytics Serving Microservice** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| A RESTful microservice providing endpoints and APIs matching the functionality of the python module. |

> **IMPORTANT:** Video Analytics Serving is provided as a _sample_. It
> is not intended to be deployed into production environments without
> modification. Developers deploying Video Analytics Serving should
> review it against their production requirements.

# Getting Started

The sample microservice includes three media analytics pipelines.

| |                  |
|---------------------------------------------|---------|
| **object_detection** | Detect and label objects such as bottles and bicycles.
| **object_classification** | Recognize attributes of vehicles within a video stream.
| **object_tracking** | Track detected objects within a video stream.
| **audio_detection** | Analyze audio streams for events such as breaking glass or barking dogs.


## Prerequisites

| |                  |
|---------------------------------------------|------------------|
| **Docker** | Video Analytics Serving requires Docker for it's build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | Video Analytics Serving's build and run scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. Instructions for macOS&reg;* users [here](docs/installing_bash_macos.md). |
| **curl** | The samples below use the `curl` command line program to issue standard HTTP requests to the microservice. Please install the latest for your platform. Note: any other tool or utility that can issue standard HTTP requests can be used in place of `curl`. |

## Building the Microservice

Build the sample microservice with the following command:

```bash
./docker/build.sh
```

The script will automatically include the sample models, pipelines and
required dependencies.

To verify the build succeeded execute the following command:

```bash
docker images video-analytics-serving-gstreamer:latest
```

Expected output:

```bash
REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
video-analytics-serving-gstreamer   latest              f51f2695639f        2 minutes ago          3.03GB
```

## Running the Microservice

Start the sample microservice with the following command:

```bash
./docker/run.sh -v /tmp:/tmp
```

This script issues a standard docker run command to launch the
container, run a Tornado based web service on port 8080, and mount the
`/tmp` folder. The `/tmp` folder is mounted to share sample
results with the host and is optional in actual deployments.

Expected output:

```
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,093", "message": "=================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,093", "message": "Loading Pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,093", "message": "=================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,588", "message": "Loading Pipelines from Config Path /home/video-analytics-serving/pipelines", "module": "pipeline_manager"}
{"levelname": "WARNING", "asctime": "2021-03-16 23:33:10,599", "message": "Missing metaconvert element", "module": "gstreamer_pipeline"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,599", "message": "Loading Pipeline: object_detection version: app_src_dst type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/app_src_dst/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,601", "message": "Loading Pipeline: object_detection version: person_vehicle_bike type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/person_vehicle_bike/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,611", "message": "Loading Pipeline: object_detection version: edgex type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/edgex/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,612", "message": "Loading Pipeline: object_detection version: 2 type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/2/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,613", "message": "Loading Pipeline: object_classification version: vehicle_attributes type: GStreamer from /home/video-analytics-serving/pipelines/object_classification/vehicle_attributes/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,616", "message": "Loading Pipeline: audio_detection version: environment type: GStreamer from /home/video-analytics-serving/pipelines/audio_detection/environment/pipeline.json", "module": "pipeline_manager"}
{"levelname": "WARNING", "asctime": "2021-03-16 23:33:10,616", "message": "Missing metaconvert element", "module": "gstreamer_pipeline"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,616", "message": "Loading Pipeline: video_decode version: app_dst type: GStreamer from /home/video-analytics-serving/pipelines/video_decode/app_dst/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,621", "message": "Loading Pipeline: object_tracking version: person_vehicle_bike type: GStreamer from /home/video-analytics-serving/pipelines/object_tracking/person_vehicle_bike/pipeline.json", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,621", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,621", "message": "Completed Loading Pipelines", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,621", "message": "===========================", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-03-16 23:33:10,702", "message": "Starting Tornado Server on port: 8080", "module": "__main__"}
```

## vaClient:

To accompany the microservice is a sample REST client which can demonstate VA Serving usages. Running the vaclient run script will quickly start a pipeline and analyze a sample
[video](https://github.com/intel-iot-devkit/sample-videos/blob/master/preview/bottle-detection.gif). Start a new shell and execute the following command:

```bash
./vaclient/vaclient.sh
```

### Pipeline Status:
As the pipeline runs, the status is queried and reported by vaclient.
> Note: When a pipeline is started, the service returns a pipeline ``instance id`` which must be used when requesting status or to stop the pipeline.
```json
Pipeline Status:

{
  "avg_fps": 98.11027534513353,
  "elapsed_time": 2.0304791927337646,
  "id": 3,
  "start_time": 1614804737.667221,
  "state": "RUNNING"
}
```

### Detection Results:
Once the pipeline run has completed, the detection results will be displayed by vaclient.

```json
{"objects":[{"detection":{"bounding_box":{"x_max":0.0503933560103178,"x_min":0.0,"y_max":0.34233352541923523,"y_min":0.14351698756217957},"confidence":0.6430817246437073,"label":"vehicle","label_id":2},"h":86,"roi_type":"vehicle","w":39,"x":0,"y":62}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":49250000000}
```

After pretty-printing:

{
  "objects": [
    {
      "detection": {
        "bounding_box": {
          "x_max":0.0503933560103178,
          "x_min":0.0,
          "y_max":0.34233352541923523,
          "y_min":0.14351698756217957
        },
        "confidence":0.6430817246437073,
        "label":"vehicle",
        "label_id":2
      },
      "h":86,
      "roi_type":"vehicle",
      "w":39,
      "x":0,
      "y":62
    }
  ],
  "resolution": {
    "height":432,
    "width":768
  },
  "source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
  "timestamp":49250000000
}
```

# More Examples

<details>

<summary>Vehicle Attributes Recognition</summary>

## Recognizing vehicle attributes in a video

### Example Request:

<table>
<tr>
<th>
Endpoint
</th>
<th>
Verb
</th>
<th>
Request
</th>
<th>
Response
</th>
</tr>
<tr>
<td>
/pipelines/object_classification/vehicle_attributes
</td>
<td>
POST
</td>
<td>
<pre lang="json">
JSON
{
  "source": {
    "uri": "https://example.mp4",
    "type": "uri"
  },
  "destination": {
    "type": "file",
    "path": "/tmp/object_classification_results.txt",
    "format": "json-lines"
  }
}
</pre>
</td>
<td>
200 <br/> <br/>
Pipeline Instance Id
</td>
</tr>
</table>

### Curl Command:

Start a new shell and execute the following command to issue an HTTP POST request, start a pipeline and analyze a sample [video](https://github.com/intel-iot-devkit/sample-videos/blob/master/preview/person-bicycle-car-detection.gif).

```bash
curl localhost:8080/pipelines/object_classification/vehicle_attributes -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
    "type": "uri"
  },
  "destination": {
    "type": "file",
    "path": "/tmp/results_object_classification.txt",
    "format": "json-lines"
  }
}'
```
### Detection Results:

To view incremental results, execute the following command from the shell.

```bash
tail -f /tmp/results_object_classification.txt
```

As the video is being analyzed and vehicle appears in frame you will see vehicle attributes in the output.

Expected Output:

```json
{"objects":[{"color":{"label":"white","model":{"name":"vehicle-attributes-recognition-barrier-0039"}},"detection":{"bounding_box":{"x_max":0.1612488180398941,"x_min":0.0,"y_max":0.3588942885398865,"y_min":0.12057243287563324},"confidence":0.9822055697441101,"label":"vehicle","label_id":2},"h":103,"roi_type":"vehicle","type":{"label":"car","model":{"name":"vehicle-attributes-recognition-barrier-0039"}},"w":124,"x":0,"y":52}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":48500000000}
```

After pretty-printing:

```json
{
  "objects": [
    {
      "color": {
        "label": "white",
        "model": {
          "name": "vehicle-attributes-recognition-barrier-0039"
        }
      },
      "detection": {
        "bounding_box": {
          "x_max":0.1612488180398941,
          "x_min":0.0,
          "y_max":0.3588942885398865,
          "y_min":0.12057243287563324
        },
        "confidence":0.9822055697441101,
        "label":"vehicle",
        "label_id":2
      },
      "h":103,
      "roi_type":"vehicle",
      "type": {
        "label":"car",
        "model": {
          "name":"vehicle-attributes-recognition-barrier-0039"
        }
      },
      "w":124,
      "x":0,
      "y":52
    }
  ],
  "resolution": {
    "height":432,
    "width":768
  },
  "source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
  "timestamp":48500000000
}
```
</details>
<details>
<summary>Audio Event Detection</summary>

## Detecting Audio Events in an Audio Recording

### Example Request:

<table>
<tr>
<th>
Endpoint
</th>
<th>
Verb
</th>
<th>
Request
</th>
<th>
Response
</th>
</tr>
<tr>
<td>
/pipelines/audio_detection/environment
</td>
<td>
POST
</td>
<td>
<pre lang="json">
JSON
{
  "source": {
    "uri": "https://example.wav",
    "type": "uri"
  },
  "destination": {
    "type": "file",
    "path": "/tmp/results_audio_events.txt",
    "format": "json-lines"
  }
}
</pre>
</td>
<td>
200 <br/> <br/>
Pipeline Instance Id
</td>
</tr>
</table>

### Curl Command:

Start a new shell and execute the following command to issue an HTTP POST request, start a pipeline and analyze a sample [audio](https://github.com/opencv/gst-video-analytics/blob/preview/audio-detect/samples/gst_launch/audio_detect/how_are_you_doing.wav?raw=true).

```bash
curl localhost:8080/pipelines/audio_detection/environment -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
    "uri": "https://github.com/opencv/gst-video-analytics/blob/preview/audio-detect/samples/gst_launch/audio_detect/how_are_you_doing.wav?raw=true",
    "type": "uri"
  },
  "destination": {
    "type": "file",
    "path": "/tmp/results_audio_events.txt",
    "format": "json-lines"
  }
}'
```

### Detection Results:

To view incremental results, execute the following command from the shell.

```bash
tail -f /tmp/results_audio_events.txt
```

As the audio is being analyzed and events are detected, you will see detection results in the output.

Expected Output:

```json
{"channels":1,"events":[{"detection":{"confidence":1.0,"label":"Speech","label_id":53,"segment":{"end_timestamp":2200000000,"start_timestamp":1200000000}},"end_timestamp":2200000000,"event_type":"Speech","start_timestamp":1200000000}],"rate":16000}
```

After pretty-printing:

```json
{
  "channels": 1,
  "events": [
    {
      "detection": {
        "confidence": 1,
        "label": "Speech",
        "label_id": 53,
        "segment": {
          "end_timestamp": 2200000000,
          "start_timestamp": 1200000000
        }
      },
      "end_timestamp": 2200000000,
      "event_type": "Speech",
      "start_timestamp": 1200000000
    }
  ],
  "rate": 16000
}
```
</details>

# Further Reading
| **Documentation** | **Reference Guides** | **Tutorials** |
| ------------    | ------------------ | ----------- |
| **-** [Defining Media Analytics Pipelines](docs/defining_pipelines.md) <br/> **-** [Building Video Analytics Serving](docs/building_video_analytics_serving.md) <br/> **-** [Running Video Analytics Serving](docs/running_video_analytics_serving.md) <br/> **-** [Customizing Pipeline Requests](docs/customizing_pipeline_requests.md) | **-** [Video Analytics Serving Architecture Diagram](docs/images/video_analytics_service_architecture.png) <br/> **-** [Microservice Endpoints](docs/restful_microservice_interfaces.md) <br/> **-** [Build Script Reference](docs/build_script_reference.md) <br/> **-** [Run Script Reference](docs/run_script_reference.md) | <br/> **-** Object Detecion Tutorials <br/> &nbsp;&nbsp;&nbsp;&nbsp; **-** [Changing Object Detection Models](docs/changing_object_detection_models.md) |

## Related Links

| **Media Frameworks** | **Media Analytics** | **Samples and Reference Designs**
| ------------    | ------------------ | -----------------|
| **-** [GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* <br/> **-** [GStreamer* Overview](docs/gstreamer_overview.md) <br/> **-** [FFmpeg](https://ffmpeg.org/)* | **-** [OpenVINO<sup>&#8482;</sup> Toolkit](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit.html) <br/> **-** [OpenVINO<sup>&#8482;</sup> Toolkit DL Streamer](https://github.com/opencv/gst-video-analytics) <br/> **-** [FFmpeg* Video Analytics](https://github.com/VCDP/FFmpeg-patch) | **-** [Open Visual Cloud Smart City Sample](https://github.com/OpenVisualCloud/Smart-City-Sample) <br/> **-** [Open Visual Cloud Ad-Insertion Sample](https://github.com/OpenVisualCloud/Ad-Insertion-Sample) <br/> **-** [Edge Insights for Retail](https://software.intel.com/content/www/us/en/develop/articles/real-time-sensor-fusion-for-loss-detection.html)


# Known Issues
Known issues are tracked on [GitHub](https://github.com/intel/video-analytics-serving/issues)*

---
\* Other names and brands may be claimed as the property of others.
