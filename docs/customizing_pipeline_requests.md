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
		"uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
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
$ curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'
2
```
The number returned on the console is the pipeline instance id (e.g. 2).

As the video is being analyzed and as events start and stop you will see detection results in the `destination` file and can be viewed using:

```bash
$ tail -f /tmp/results.txt
{"objects":[{"detection":{"bounding_box":{"x_max":0.9022353887557983,"x_min":0.7940621376037598,"y_max":0.8917602300643921,"y_min":0.30396613478660583},"confidence":0.7093080282211304,"label":"bottle","label_id":5},"h":212,"roi_type":"bottle","w":69,"x":508,"y":109}],"resolution":{"height":360,"width":640},"source":"https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true","timestamp":39553072625}
```

### RTSP Source
In real world the media `source` would most likely be from live IP camera feeds or rtsp streams. RTSP url's will normally be of the format `rtsp://<ip_address>:<port>/<server_url>`. 

In this example we will use `rtsp://192.142.192.142:8654/simulated_camera.sdp` as rtsp url. The request object would now look like:
```json
{
	"source": {
		"uri": "rtsp://192.142.192.142:8654/simulated_camera.sdp",
		"type": "uri"
	},
	"destination": {
		"type": "file",
		"path": "/tmp/results.txt",
		"format": "json-lines"
	}
}
```
A sample request to start an object detection pipeline with `source` from this rtsp stream can be initiated using the following command:
```bash
$ curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "rtsp://192.142.192.142:8654/simulated_camera.sdp", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'
3
```

Detection results from executing the above pipeline will be stored in the `destination` file and can be viewed using:
```bash
$ tail -f /tmp/results.txt
{"objects":[{"detection":{"bounding_box":{"x_max":0.7214203476905823,"x_min":0.5804712176322937,"y_max":0.7988698482513428,"y_min":0.5221277475357056},"confidence":0.5024334192276001,"label":"tvmonitor","label_id":20},"h":299,"roi_type":"tvmonitor","w":271,"x":1115,"y":564}],"resolution":{"height":1080,"width":1920},"source":"rtsp://192.142.192.142:8654/simulated_camera.sdp","timestamp":424246323158}
```

With an rtsp stream as source, the pipeline keeps running as long as the rtsp stream is live. 
To get the status of pipeline instance with an instance id for e.g. 3, execute the below command:
```bash
$ curl localhost:8080/pipelines/object_detection/1/3/status -X GET
{
  "avg_fps": 56.52932122000287,
  "elapsed_time": 18.08210277557373,
  "id": 3,
  "start_time": 1596174349.5461419,
  "state": "RUNNING"
}
```
`id` here is the pipeline instance id.

To stop the pipeline instance with an instance id for e.g. 3, execute the below command:
```bash
$ curl localhost:8080/pipelines/object_detection/1/3 -X DELETE
```

> **NOTE:** The below sections are TBD and will be expanded later.

###  Web Camera Source

## Destination

### File

### MQTT

### KAFKA

## Parameters 


