# VA Client Command Reference
vaclient is a python app intended to be a reference for using VA Serving REST API. vaclient is included in the main container and can be easily launched using the accompanying run script, `vaclient.sh`.

>**Note:**
This document assumes you are familiar with vaserving. See the main [README](../README.md) for details on building and running the service.

## Basic Usage
### Listing Supported Pipelines and Models
To see which models and pipelines are loaded by the service run the following commands. Both models and pipelines are displayed in the tuplet form of name/version.
> **Note:** Results will vary depending on your service configuration

Fist models:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh list-models
<snip>
 - emotion_recognition/1
 - object_detection/1
 - object_detection/person_vehicle_bike
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - face_detection_retail/1
 ```

Now pipelines:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh list-pipelines
<snip>
 - audio_detection/environment
 - object_classification/vehicle_attributes
 - video_decode/app_dst
 - object_detection/app_src_dst
 - object_detection/person_vehicle_bike
 - object_tracking/person_vehicle_bike
```

### Running Pipelines
vaclient can be used to send pipeline start requests using the `run` command. With the `run` command you will need to enter two additional arguments the `pipeline` (in the form of pipeline_name/pipeline_version) you wish to use and the `uri` pointing to the media of your choice.
```
~/video-analytics-serving$ ./vaclient/vaclient.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
As the pipeline runs, the output file is processed by vaclient and inference information is printed to the screen in the following format: `label (confidence) [top left width height] {meta-data}` At the end of the pipeline run, the average fps is printed as well. If you wish to stop the pipeline mid-run, `Ctrl+C` will signal the client to send a `stop` command to the service. Once the pipeline is stopped, vaclient will output the average fps. More on `stop` below

```
Timestamp 48583333333
- vehicle (0.95) [0.00, 0.12, 0.15, 0.36] {}
Timestamp 48666666666
- vehicle (0.79) [0.00, 0.12, 0.14, 0.36] {}
Timestamp 48833333333
- vehicle (0.68) [0.00, 0.13, 0.11, 0.36] {}
Timestamp 48916666666
- vehicle (0.78) [0.00, 0.13, 0.10, 0.36] {}
Timestamp 49000000000
- vehicle (0.63) [0.00, 0.13, 0.09, 0.36] {}
Timestamp 49083333333
- vehicle (0.63) [0.00, 0.14, 0.07, 0.35] {}
Timestamp 49166666666
- vehicle (0.69) [0.00, 0.14, 0.07, 0.35] {}
Timestamp 49250000000
- vehicle (0.64) [0.00, 0.14, 0.05, 0.34] {}
avg_fps: 39.66
```
### Starting Pipelines
The `run` command is helpful for quickly showing inference results but `run` blocks until completion. If you want to do your own processing and only want to kickoff a pipeline, this can be done with the `start` command. `start` arguments are the same as `run`, you'll need to provide the `pipeline` and `uri`. Run the following command:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
#### Instance ID
On a successful start of a pipeline, vaserving assigns a pipeline `instance_id` which is a unique number which can be used to reference the pipeline in subsequent requests. In this example, the `instance_id` is `1`
```
Starting pipeline...
Pipeline running: object_detection/person_vehicle_bike, instance = 1
```
### Stopping Pipelines
Stopping a pipeline can be accomplished using the `stop` command along with the `pipeline` and `instance id`:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh stop object_detection/person_vehicle_bike 1
```
Expected output: Average fps also printed for stopped pipeline.
```
Stopping Pipeline...
Pipeline stopped
avg_fps: 42.07
```
### Getting Pipeline Status
Querying the current state of the pipeline is done using the `status` command along with the `pipeline` and `instance id`:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh status object_detection/person_vehicle_bike 1
```
vaclient will print the status of either `QUEUED`, `RUNNING`, `ABORTED`, or `COMPLETED`

### Waiting for a pipeline to finish
If you wish to wait for a pipeline to finish running you can use the `wait` command along with the `pipeline` and `instance id`:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh wait object_detection/person_vehicle_bike 1
```
The client will print the inital status of the pipeline. Then wait for completion and print the average fps.


## Command Options
As described in [customizing pipeline requests](../docs/customizing_pipeline_requests.md), pipeline request options can be customized. This section describes ways to customize vaclient `run` and `start` commands.

### --destination
By default, vaclient uses a generic template for destination:
```json
{
"destination": {
	"metadata": {
		"type": "file",
		"path": "/tmp/results.jsonl",
		"format": "json-lines"
	}
}}
```
Destination configuration can be updated with `--destination`. For example, passing in `--destination path /new/filepath/results.jsonl` will update filepath for results saving (Note you may need to volume mount this new location when running vaserving.)

### --parameter
By default, vaclient relies on pipeline parameter defaults. This can be updated with `--parameter` option. For exmaple add `--parameter detection-device GPU`

### --rtsp-path
If you are utiziling RTSP restreaming, `--rtsp-path` can be used to update the `server_url` path.
For example, adding `--rtsp-path new_path` will able you to view the stream at `rtsp://<ip_address>:<port>/new_path`. More details on RTSP restreaming in [running_video_analytics_serving](../docs/running_video_analytics_serving.md) documentation.

### --show-request
All vaclient commands can be used with the `--show-request` option which will print out the HTTP request but will not send. Here are some examples:

#### Run:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --show-request
<snip>
POST http://localhost:8080/pipelines/object_detection/person_vehicle_bike
Body:{'source': {'uri': 'https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true', 'type': 'uri'}, 'destination': {'metadata': {'type': 'file', 'path': '/tmp/results.jsonl', 'format': 'json-lines'}}}
```

#### Stop:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh stop object_detection/person_vehicle_bike 1 --show-request
<snip>
DELETE http://localhost:8080/pipelines/object_detection/person_vehicle_bike/1
```

#### Status:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh status object_detection/person_vehicle_bike 1 --show-request
<snip>
GET http://localhost:8080/pipelines/object_detection/person_vehicle_bike/1/status
```
