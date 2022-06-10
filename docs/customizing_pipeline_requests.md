# Customizing Pipeline Requests
| [Request Format](#request-format) | [Source](#source) | [Destination](#metadata-destination) | [Parameters](#parameters) | [Tags](#tags) |

Pipeline requests are initiated to exercise the Intel® Deep Learning Streamer (Intel® DL Streamer) Pipeline Server REST API. Each pipeline in the Pipeline Server has a specific endpoint. A pipeline can be started by issuing a `POST` request and a running pipeline can be stopped using a `DELETE` request. The `source` and `destination` elements of Pipeline Server [pipeline templates](defining_pipelines.md#pipeline-templates) are configured and constructed based on the `source` and `destination` from the incoming requests.

## Request Format

> Note: This document shows curl requests. Requests can also be sent via pipeline_client using the --request-file option see [Pipeline Client Command Options](../client/README.md#command-options)

Pipeline requests sent to Pipeline Server REST API are JSON documents that have the following attributes:

|Attribute | Description |
|---------|-----|
|`source`| Required attribute specifying the video source that needs to be analyzed. It consists of : <br>    `uri` : the uri of the video source that needs to be analyzed <br>    `type` : is the value `uri` |
|`destination`| Optional attribute specifying the output to which analysis results need to be sent/saved. It consists of `metadata` and `frame`|
|`parameters`| Optional attribute specifying pipeline parameters that can be customized when the pipeline is launched.|
|`tags`| Optional attribute specifying a JSON object of additional properties that will be added to each frame's metadata.|

### Example Request
Below is a sample request using curl to start an `object_detection/person_vehicle_bike` pipeline that analyzes the video [person-bicycle-car-detection.mp4](https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4) and sends its results to `/tmp/results.json`.

> Note: Files specified as a source or destination need to be accessible from within the Pipeline Server container. Local files and directories can be volume mounted using standard docker runtime options. As an example the following command launches a Pipeline Server container with the local `/tmp` directory volume mounted. Results to `/tmp/results.jsonl` are persisted after the container exits.
> ```bash
> docker/run.sh -v /tmp:/tmp
> ```

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.jsonl",
            "format": "json-lines"
        }
    },
    "parameters":{
        "threshold": 0.90
   }
}'
```
```
2
```

The number returned on the console is the pipeline instance id (e.g. 2).
As the video is being analyzed and as objects are detected, results are added to the `destination` file which can be viewed using:

```bash
tail -f /tmp/results.jsonl
```
```
{"objects":[{"detection":{"bounding_box":{"x_max":0.7503407597541809,"x_min":0.6836109757423401,"y_max":0.9968345165252686,"y_min":0.7712376117706299},"confidence":0.93408203125,"label":"person","label_id":1},"h":97,"roi_type":"person","w":51,"x":525,"y":333}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1916666666}
{"objects":[{"detection":{"bounding_box":{"x_max":0.7554543018341064,"x_min":0.6827328205108643,"y_max":0.9928492903709412,"y_min":0.7551988959312439},"confidence":0.92578125,"label":"person","label_id":1},"h":103,"roi_type":"person","w":56,"x":524,"y":326}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":2000000000}
<snip>
```

## Source
The `source` attribute specifies the video source that needs to be analyzed. It can be changed to use media from different sources.
Some of the common video sources are:

* File Source
* IP Camera (RTSP Source)
* Web Camera

> Note: See [Source Abstraction](./defining_pipelines.md#source-abstraction) to learn about GStreamer source elements set per request.

### File Source
The following example shows a media `source` from a video file in GitHub:

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.jsonl",
            "format": "json-lines"
        }
    }
}'
```

A local file can also be used as a source. In the following example person-bicycle-car-detection.mp4 has been downloaded to /tmp and Pipeline Server was started as:
```bash
docker/run.sh -v /tmp:/tmp
```
```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "file:///tmp/person-bicycle-car-detection.mp4",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.jsonl",
            "format": "json-lines"
        }
    }
}'
```

### RTSP Source
RTSP streams from IP cameras can be referenced using the `rtsp` uri scheme. RTSP uris will normally be of the format `rtsp://<user>:<password>@<ip_address>:<port>/<server_url>` where `<user>` and `password` are optional authentication credentials.

The request `source` object would be updated to:

```json
{
    "source": {
        "uri": "rtsp://<ip_address>:<port>/<server_url>",
        "type": "uri"
    }
}
```

### Web Camera Source
Web cameras accessible through the `Video4Linux` api and device drivers are supported via `type=webcam`. `device` is the path of the `v4l2` device, typically `video<N>`.

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
      "device": "/dev/video0",
      "type": "webcam"
    },
    "destination": {
        "metadata": {
          "type": "file",
          "path": "/tmp/results.jsonl",
          "format": "json-lines"
        }
    }
}'
```

## Setting source properties
For any of the sources mentioned above, it is possible to set properties on the source element via the request.

### Setting a property on source bin element
For example, to set property `buffer-size` on urisourcebin, source section can be set as follows:
```json
{
    "source": {
        "uri": "file:///tmp/person-bicycle-car-detection.mp4",
        "type": "uri",
        "properties": {
            "buffer-size": 4096
        }
    }
}
```

### Setting a property on underlying element
For example, if you'd like to set `ntp-sync` property of the `rtspsrc` element to synchronize timestamps across RTSP source(s).

> Note: This feature, enabled via GStreamer `source-setup` callback signal is only supported for `urisourcebin` element.

```json
{
    "source": {
        "uri": "rtsp://<ip_address>:<port>/<server_url>",
        "type": "uri",
        "properties": {
            "ntp-sync": true
        }
    }
}
```

## Metadata Destination
Pipelines can optionally be configured to output metadata to a specific destination.

For metadata, the destination type can be set to file, mqtt, or kafka as needed.


### File
The following are available properties:
- type : "file"
- path (required): Path to the file.
- format (optional): Format can be of the following types (default is json):
  - json-lines : Each line is a valid JSON.
  - json : Entire file is formatted as a JSON.

Below is an example for JSON format

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.json",
            "format": "json"
        }
    }
}'
```

### MQTT
The following are available properties:
- type : "mqtt"
- host (required) expects a format of host:port
- topic (required) MQTT topic on which broker messages are sent
- timeout (optional) Broker timeout
- mqtt-client-id (optional) Unique identifier for the MQTT client

Steps to run MQTT:
  1. Start the MQTT broker, here we use [Eclipse Mosquitto](https://hub.docker.com/_/eclipse-mosquitto/), an open source message broker.
  ```bash
  docker run --network=host eclipse-mosquitto:1.6
  ```
  2. Start the Pipeline Server with host network enabled
  ```bash
  docker/run.sh -v /tmp:/tmp --network host
  ```
  3. Send the REST request : Using the default 1883 MQTT port.
  ```bash
  curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
  'Content-Type: application/json' -d \
  '{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "mqtt",
            "host": "localhost:1883",
            "topic": "pipeline-server",
            "mqtt-client-id": "gva-meta-publish"
        }
    }
  }'
  ```
  4. Connect to MQTT broker to view inference results
  ```bash
  docker run -it --network=host --entrypoint mosquitto_sub eclipse-mosquitto:1.6 --topic pipeline-server --id mosquitto-sub
  ```

  ```bash
  {"objects":[{"detection":{"bounding_box":{"x_max":1.0,"x_min":0.11904853582382202,"y_max":0.9856844246387482,"y_min":0.019983917474746704},"confidence":0.5811731815338135,"label":"vehicle","label_id":2},"h":417,"roi_type":"vehicle","w":677,"x":91,"y":9}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":13916666666}
  {"objects":[{"detection":{"bounding_box":{"x_max":0.3472719192504883,"x_min":0.12164716422557831,"y_max":1.0,"y_min":0.839308500289917},"confidence":0.6197869777679443,"label":"vehicle","label_id":2},"h":69,"roi_type":"vehicle","w":173,"x":93,"y":363}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":14333333333}
  {"objects":[{"detection":{"bounding_box":{"x_max":0.3529694750905037,"x_min":0.12145502120256424,"y_max":1.0,"y_min":0.8094810247421265},"confidence":0.7172137498855591,"label":"vehicle","label_id":2},"h":82,"roi_type":"vehicle","w":178,"x":93,"y":350}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":14416666666}
  ```
  5. In the MQTT broker terminal, you should see the connection from client with specified `mqtt-client-id`
  ```
  <snip>
  1632949258: New connection from 127.0.0.1 on port 1883.
  1632949258: New client connected from 127.0.0.1 as gva-meta-publish (p2, c1, k20).
  1632949271: New connection from 127.0.0.1 on port 1883.
  1632949271: New client connected from 127.0.0.1 as mosquitto-sub (p2, c1, k60).
  1632949274: Client gva-meta-publish disconnected.
  ```

### Kafka
The following properties are available for the Apache Kafka destination:
- type : "kafka"
- host (required) expects a format of host:port
- topic (required) Kafka topic on which broker messages are sent

Steps to run Kafka:
1. Prepare to run a Kafka broker. Since Kafka relies on ZooKeeper for management, let's create `docker-compose-kafka.yml` with the following content:

   ```bash
   version: "2"
   services:
     zookeeper:
       image: docker.io/bitnami/zookeeper:3.7
       ports:
         - "2181:2181"
       volumes:
         - "zookeeper_data:/bitnami"
       environment:
         - ALLOW_ANONYMOUS_LOGIN=yes
     kafka:
       image: docker.io/bitnami/kafka:2
       ports:
         - "9092:9092"
       volumes:
         - "kafka_data:/bitnami"
       environment:
         - KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true
         - KAFKA_CFG_ZOOKEEPER_CONNECT=zookeeper:2181
         - KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
         - ALLOW_PLAINTEXT_LISTENER=yes
       depends_on:
         - zookeeper
   volumes:
     zookeeper_data:
       driver: local
     kafka_data:
       driver: local
   ```

2. Run the following command to launch Kafka broker as a detached service:
   ```bash
   docker-compose -p pipeline-server -f docker-compose-kafka.yml up -d
   ```

3. Start the Pipeline Server with host network enabled:
   ```bash
   docker/run.sh -v /tmp:/tmp --network host
   ```

4. Launch pipeline with parameters to emit on the Kafka topic we are listening for:
```
  curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
  'Content-Type: application/json' -d \
  '{
      "source": {
          "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
          "type": "uri"
      },
      "destination": {
          "metadata": {
               "type": "kafka",
               "format": "json-lines",
               "host": "localhost",
               "port": 9092,
               "topic": "pipeline-server.person_vehicle_bike"
            }
        }
    }'
  ```

5. Connect to Kafka broker to view inference results:
   ```bash
   docker exec -it pipeline-server_kafka_1 /opt/bitnami/kafka/bin/kafka-console-consumer.sh \
      --bootstrap-server localhost:9092 --topic pipeline-server.person_vehicle_bike
   ```

   ```bash
   {"objects":[{"detection":{"bounding_box":{"x_max":0.7448995113372803,"x_min":0.6734093427658081,"y_max":0.9991495609283447,"y_min":0.8781012296676636},"confidence":0.5402464866638184,"label":"person","label_id":1},"h":52,"roi_type":"person","w":55,"x":517,"y":379}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1500000000}
   {"objects":[{"detection":{"bounding_box":{"x_max":0.7442193031311035,"x_min":0.6763269901275635,"y_max":1.0,"y_min":0.8277983069419861},"confidence":0.5505848526954651,"label":"person","label_id":1},"h":74,"roi_type":"person","w":52,"x":519,"y":358}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1666666666}
   {"objects":[{"detection":{"bounding_box":{"x_max":0.7465137243270874,"x_min":0.6821863651275635,"y_max":1.0,"y_min":0.810469388961792},"confidence":0.6447391510009766,"label":"person","label_id":1},"h":82,"roi_type":"person","w":49,"x":524,"y":350}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1750000000}
   {"objects":[{"detection":{"bounding_box":{"x_max":0.7481285929679871,"x_min":0.6836653351783752,"y_max":0.9999656677246094,"y_min":0.7867168188095093},"confidence":0.8825281858444214,"label":"person","label_id":1},"h":92,"roi_type":"person","w":50,"x":525,"y":340}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1833333333}
   ```

6. NOTE: When finished, remember to close running containers with this command:
   ```bash
   docker-compose -f docker-compose-kafka.yml down
   ```

## Frame Destination
`Frame` is another type of destination that sends frames with superimposed bounding boxes over either RTSP or WebRTC protocols.

### RTSP
RTSP functionality must be enabled in Pipeline Server for this feature to be used, see [RTSP re-streaming](running_pipeline_server.md#real-time-streaming-protocol-rtsp-re-streaming).

Steps for visualizing output over RTSP assuming Pipeline Server and your VLC client are running on the same host.

1. Start a pipeline with  frame destination type set as `rtsp` and an endpoint path `person-detection`.
```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "format": "json-lines",
            "path": "/tmp/results.jsonl"
        },
        "frame": {
            "type": "rtsp",
            "path": "person-detection"
        }
    }
}'
```
2. Use an RTSP client such as VLC to visualize the stream at address `rtsp://localhost:8554/person-detection`.

> **Note:** Use Pipeline Server Client's [--rtsp-path](../client/README.md#--rtsp-path) argument to specific RTSP output endpoint.

The following parameters can be optionally used to customize the stream:
- path (required): custom string to uniquely identify the stream
- cache-length (default 30): number of frames to buffer in rtsp pipeline.
- encoding-quality (default 85): jpeg encoding quality (0 - 100). Lower values increase compression but sacrifice quality.
- sync-with-source (default True): rate limit processing pipeline to encoded frame rate (e.g. 30 fps)
- sync-with-destination (default True): block processing pipeline if rtsp pipeline is blocked.

> **Note:** If the RTSP stream playback is choppy this may be due to
> network bandwidth. Decreasing the encoding-quality or increasing the
> cache-length can help.

### WebRTC
WebRTC must be enabled for these request parameters to be accepted. For more information, see [WebRTC streaming](running_pipeline_server.md#web-real-time-communication-webrtc).

#### Request WebRTC Frame Output
1. Start a pipeline to request frame destination type set as WebRTC and unique `peer-id` value set. For demonstration, peer-id is set as `person_detection_001` in example request below.

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "format": "json-lines",
            "path": "/tmp/results.jsonl"
        },
        "frame": {
            "type": "webrtc",
            "peer-id": "person_detection_001"
        }
    }
}'
```
2. Check that pipeline is running using [status request](restful_microservice_interfaces.md#get-pipelinesnameversioninstance_id) before trying to connect the WebRTC peer.
3. View the pipeline stream in your browser with url `http://localhost:8082/?destination_peer_id=person_detection_001&instance_id=e98dae1caf7511ecaaf90242ac170004` where the value of `destination_peer_id` query parameter matches the `--webrtc-peer-id` provided in the request from step 1 and the value of `instance_id` is produced in the response from step 1.

> **Note:** Use Pipeline Server Client's [--webrtc-peer-id](../client/README.md#--webrtc-peer-id) argument to specify peer id.

#### WebRTC Destination Parameters
Use the following parameters to customize the request:
- type : "webrtc"
- peer-id (required): custom string to uniquely identify the stream. May contain alphanumeric or underscore `_` characters only.
- cache-length (default 30): number of frames to buffer in WebRTC pipeline.
- cq-level (default 10): vp8 constrained encoding quality level (0 - 63). Lower values increase compression but sacrifice quality. Explanation and related details found on this [encoder parameter guide](https://www.webmproject.org/docs/encoder-parameters/).
- sync-with-source (default True): rate limit processing pipeline to encoded frame rate (e.g. 30 fps)
- sync-with-destination (default True): block processing pipeline if WebRTC pipeline is blocked.

> **Note:** If WebRTC stream playback is choppy this may be due to
> network bandwidth. Decreasing the encoding-quality or increasing the
> cache-length can help.

> **Note:** Providing an invalid value to Pipeline Client for `--webrtc-peer-id` will output a 400 "Invalid Destination" error.

## Parameters
Pipeline parameters as specified in the pipeline definition file, can be set in the REST request.
For example, below is a pipeline definition file:

```json
{
	"type": "GStreamer",
	"template": ["uridecodebin name=source",
				" ! gvadetect model={models[object_detection][person_vehicle_bike][network]} name=detection",
				" ! gvametaconvert name=metaconvert ! gvametapublish name=destination",
				" ! appsink name=appsink"
			],
	"description": "Person Vehicle Bike Detection based on person-vehicle-bike-detection-crossroad-0078",
	"parameters": {
		"type": "object",
		"properties": {
			"detection-device": {
				"element": {
					"name": "detection",
					"property": "device"
				},
				"type": "string"
			},
			"detection-model-instance-id": {
				"element": {
					"name": "detection",
					"property": "model-instance-id"
				},
				"type": "string"
			},
			"inference-interval": {
				"element": "detection",
				"type": "integer"
			},
			"threshold": {
				"element": "detection",
				"type": "number"
			}
		}
	}
}
```

Any or all of the parameters defined i.e detection-device, detection-model-instance-id, inference-interval and threshold can be set via the request.

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
  "source": {
      "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type": "uri"
  },
  "destination": {
      "metadata": {
          "type": "file",
          "path": "/tmp/results.jsonl",
          "format": "json-lines"
      }
  },
  "parameters": {
      "detection-device": "GPU",
      "detection-model-instance-id": "1",
      "threshold": 0.90
  }
}'
```

For the example above as threshold was set to 0.90 (default value 0.5), the metadata would only contain results where the confidence exceeds 0.90

```json
{"objects":[{"detection":{"bounding_box":{"x_max":0.7503407597541809,"x_min":0.6836109757423401,"y_max":0.9968345165252686,"y_min":0.7712376117706299},"confidence":0.93408203125,"label":"person","label_id":1},"h":97,"roi_type":"person","w":51,"x":525,"y":333}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":1916666666}
{"objects":[{"detection":{"bounding_box":{"x_max":0.7554543018341064,"x_min":0.6827328205108643,"y_max":0.9928492903709412,"y_min":0.7551988959312439},"confidence":0.92578125,"label":"person","label_id":1},"h":103,"roi_type":"person","w":56,"x":524,"y":326}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":2000000000}
{"objects":[{"detection":{"bounding_box":{"x_max":0.7566969394683838,"x_min":0.683247447013855,"y_max":0.9892041087150574,"y_min":0.7453113198280334},"confidence":0.95263671875,"label":"person","label_id":1},"h":105,"roi_type":"person","w":56,"x":525,"y":322}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":2083333333}
{"objects":[{"detection":{"bounding_box":{"x_max":0.7583206295967102,"x_min":0.6872420907020569,"y_max":0.9740238189697266,"y_min":0.7231987714767456},"confidence":0.95947265625,"label":"person","label_id":1},"h":108,"roi_type":"person","w":55,"x":528,"y":312}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":2166666666}

```
For more details on parameters, see [Pipeline Parameters](defining_pipelines.md#pipeline-parameters)

## Tags

Tags are pieces of information specified at the time of request, stored with frames metadata. In the example below, tags are used to describe the location and orientation of video input.

```bash
curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
'Content-Type: application/json' -d \
'{
    "source": {
        "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.json",
            "format": "json"
        }
    },
    "tags": {
        "camera_location": "parking_lot",
        "direction" : "east"
    }
}'
```

Inference results are updated with tags

```json
{
  "objects": [
      {
          "detection": {
              "bounding_box": {
                  "x_max": 0.7448995113372803,
                  "x_min": 0.6734093427658081,
                  "y_max": 0.9991495609283447,
                  "y_min": 0.8781012296676636
              },
              "confidence": 0.5402464866638184,
              "label": "person",
              "label_id": 1
          },
          "h": 52,
          "roi_type": "person",
          "w": 55,
          "x": 517,
          "y": 379
      }
  ],
  "resolution": {
      "height": 432,
      "width": 768
  },
  "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
  "tags": {
      "camera_location": "parking_lot",
      "direction": "east"
  },
  "timestamp": 1500000000
}
```
