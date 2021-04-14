# Customizing Video Analytics Pipeline Requests
| [Request Format](#request-format) | [Source](#source) | [Destination](#destination) | [Parameters](#parameters) |

Pipeline requests are initiated to exercise the Video Analytics Serving REST-API. Each pipeline in VA Serving has a specific endpoint. A pipeline can be started by issuing a `POST` request and a running pipeline can be stopped using a `DELETE` request. The `source` and `destination` elements of VA Serving [pipeline templates](./defining_pipelines.md#pipeline_templates) are configured and constructed based on the `source` and `destination` from the incoming requests.

## Request Format
Pipeline requests sent to Video Analytics Serving REST-API are json documents that have the following attributes:

|Attribute | Description |
|---------|-----|
|`source`|The video source that needs to be analyzed. It consists of - <br> 	`uri` : the uri of the video source that needs to be analyzed <br> 	`type` : is the value `uri` |
|`destination`|The output to which analysis results need to be send/saved. It consists of `type`, `path` and `format`. |
|`parameters`|Optional attribute specifying pipeline parameters that can be customized when the pipeline is launched.|

### Example Request:
```json
{
	"source": {
		"uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
		"type": "uri"
	},
	"destination": {
		"type": "file",
		"path": "/tmp/results.txt",
		"format": "json-lines"
	},
	"parameters":{
		"height":300,
		"width":300
	}
}
```

## Source

The `source` attribute specifies the video source that needs to be analyzed. It can be changed to use media from different sources.
Some of the common video sources are:
* File Source
* IP Camera (RTSP Source)
* Web Camera

### File Source
The example request shown in above section has media `source` from a video file checked in github. With the service running, you can use curl command line program to start an object detection pipeline with video source from a video file as follows:
```bash
$ curl localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'
2
```
The number returned on the console is the pipeline instance id (e.g. 2).

As the video is being analyzed and as events start and stop you will see detection results in the `destination` file and can be viewed using:

```bash
$ tail -f /tmp/results.txt
{"objects":[{"detection":{"bounding_box":{"x_max":0.0503933560103178,"x_min":0.0,"y_max":0.34233352541923523,"y_min":0.14351698756217957},"confidence":0.6430817246437073,"label":"vehicle","label_id":2},"h":86,"roi_type":"vehicle","w":39,"x":0,"y":62}],"resolution":{"height":432,"width":768},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true","timestamp":49250000000}
```

### RTSP Source
In real world the media `source` would most likely be from live IP camera feeds or rtsp streams. RTSP url's will normally be of the format `rtsp://<ip_address>:<port>/<server_url>`. The request `source` object would be updated to:
```json
{
	"source": {
		"uri": "rtsp://<ip_address>:<port>/<server_url>",
		"type": "uri"
	}
}
```


> **NOTE:** The below sections are TBD and will be expanded later.

###  Web Camera Source

## Destination

### File

### MQTT

### KAFKA

## Parameters
