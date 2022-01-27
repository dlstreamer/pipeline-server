# VA Client Command Reference
vaclient is a python app intended to be a reference for using VA Serving REST API. vaclient is included in the main container and can be easily launched using the accompanying run script, `vaclient.sh`.

>**Note:**
This document assumes you are familiar with VA Serving. See the main [README](../README.md) for details on building and running the service.

## Basic Usage
### Listing Supported Pipelines and Models
To see which models and pipelines are loaded by the service run the following commands. Both models and pipelines are displayed in the tuplet form of name/version.
> **Note:** Results will vary depending on your service configuration

First models:
```
 ./vaclient/vaclient.sh list-models
```
```
<snip>
 - emotion_recognition/1
 - object_detection/person_vehicle_bike
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - face_detection_retail/1
 ```

Now pipelines:
```
./vaclient/vaclient.sh list-pipelines
```
```
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
./vaclient/vaclient.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
If the pipeline request is successful, an instance id is created and vaclient will print the instance. More on `instance_id` below.
Once pre-roll is completed and pipeline begins running, the output file is processed by vaclient and inference information is printed to the screen in the following format: `label (confidence) [top left width height] {meta-data}` At the end of the pipeline run, the average fps is printed as well. If you wish to stop the pipeline mid-run, `Ctrl+C` will signal the client to send a `stop` command to the service. Once the pipeline is stopped, vaclient will output the average fps. More on `stop` below

```
Pipeline instance = <uuid>
Pipeline running
<snip>
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
However, if there are errors during pipeline execution i.e GPU is specified as detection device but is not present, vaclient will terminate with an error message
```
Pipeline instance = <uuid>
Error in pipeline, please check pipeline-server log messages
```

### Starting Pipelines
The `run` command is helpful for quickly showing inference results but `run` blocks until completion. If you want to do your own processing and only want to kickoff a pipeline, this can be done with the `start` command. `start` arguments are the same as `run`, you'll need to provide the `pipeline` and `uri`. Run the following command:
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
Similar to `run`, if the pipeline request is successful, an instance id is created and vaclient will print the instance. More on `instance_id` below.
```
Pipeline instance = <uuid>
```
Errors during pipeline execution are not flagged as vaclient exits after receiving instance id for a successful request. However, both `start` and `run` will flag invalid requests, for example:
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bke https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
The pipeline name has a typo `object_detection/person_vehicle_bke` making it invalid, this results in the error message:
```
Got unsuccessful status code: 400
"Invalid Pipeline or Version"

Pipeline failed to start
```

#### Instance ID
On a successful start of a pipeline, VA Serving assigns a pipeline `instance_id` which is a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) which can be used to reference the pipeline in subsequent requests. In this example, the `instance_id` is `0fe8f408ea2441bca8161e1190eefc51`
```
Starting pipeline object_detection/person_vehicle_bike, instance = 0fe8f408ea2441bca8161e1190eefc51
```
### Stopping Pipelines
Stopping a pipeline can be accomplished using the `stop` command along with the `pipeline` and `instance id`:
```
./vaclient/vaclient.sh stop object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
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
./vaclient/vaclient.sh status object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
```
vaclient will print the status of `QUEUED`, `RUNNING`, `ABORTED`, `COMPLETED` or `ERROR` like so
```
<snip>
RUNNING
```

### Waiting for a pipeline to finish
If you wish to wait for a pipeline to finish running you can use the `wait` command along with the `pipeline` and `instance id`:
```
./vaclient/vaclient.sh wait object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
```
The client will print the initial status of the pipeline. Then wait for completion and print the average fps.

### Getting Status of All Pipelines
Querying the current state of the pipeline is done using the `list-instances` command.

This example starts two pipelines and then gets their status and request details.
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
```
Starting pipeline object_detection/person_vehicle_bike, instance = 94cf72b718184615bfc181c6589b240c
```
```
./vaclient/vaclient.sh start object_classification/vehicle_attributes https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true
```
```
Starting pipeline object_classification/vehicle_attributes, instance = 978e09c561f14fa1b793e8b644f30031
```
```
./vaclient/vaclient.sh list-instances
```
```
01: object_detection/person_vehicle_bike
state: RUNNING
fps: 16.74
source: {
    "element": "urisourcebin",
    "type": "uri",
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true"
}
destination: {
    "metadata": {
        "format": "json-lines",
        "path": "/tmp/results.jsonl",
        "type": "file"
    }
}

02: object_classification/vehicle_attributes
state: RUNNING
fps: 11.08
source: {
    "element": "urisourcebin",
    "type": "uri",
    "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true"
}
destination: {
    "metadata": {
        "format": "json-lines",
        "path": "/tmp/results.jsonl",
        "type": "file"
    }
}
parameters: {
    "object-class": "vehicle"
}
```

## Command Line Arguments
See [customizing pipeline requests](../docs/customizing_pipeline_requests.md) to further understand how pipeline request options can be customized.

### --quiet
This optional argument is meant to handle logging verbosity common across all commands to vaclient.
> **Note**: If specified, --quiet needs to be placed ahead of the specific command i.e start, run etc.

#### Start
vaclient output will just be the pipeline instance.
```
./vaclient/vaclient.sh --quiet start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
```
<snip>
2
```
#### Run
vaclient output will be the pipeline instance followed by inference results.
```
./vaclient/vaclient.sh --quiet run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
```
<snip>
1
Timestamp 1500000000
- person (0.54) [0.67, 0.88, 0.74, 1.00]
Timestamp 1666666666
- person (0.55) [0.68, 0.83, 0.74, 1.00]
```

### Run/Start Arguments
This section summarizes all the arguments for vaclient `run` and `start` commands.

#### pipeline (required)
Positional argument (first) that specifies the pipeline to be launched in the form of `pipeline name/pipeline version`.

#### uri (optional)
Positional argument (second) that specifies the location of the content to play/analyze.
> Note: uri argument can be skipped only if passed in via --request-file

#### --destination
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
Destination configuration can be updated with `--destination`. This argument affects only metadata part of the destination.
In the following example, passing in `--destination path /tmp/newfile.jsonl` will update the filepath for saving inference result.
> **Note**: You may need to volume mount this new location when running VA Serving.
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --destination path /tmp/newfile.jsonl
```

#### --rtsp-path
If you are utilizing RTSP restreaming, `--rtsp-path` can be used to update the `server_url` path. This updates the frame part of destination under the hood.
For example, adding `--rtsp-path new_path` will able you to view the stream at `rtsp://<ip_address>:<port>/new_path`. More details on RTSP restreaming in [running_video_analytics_serving](../docs/running_video_analytics_serving.md) documentation.

#### --parameter
By default, vaclient relies on pipeline parameter defaults. This can be updated with `--parameter` option. See [Defining Pipelines](../docs/defining_pipelines.md) to know how parameters are defined. The following example adds `--parameter detection-device GPU`
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --parameter detection-device GPU
```

#### --parameter-file
Specifies a JSON file that contains parameters in key, value pairs. Parameters from this file take precedence over those set by `--parameter`.
> **Note**: As vaclient volume mounts /tmp, the parameter file may be placed there.

A sample parameter file can look like
```json
{
    "parameters": {
        "detection-device": "GPU"
    }
}
```
The above file, say /tmp/sample_parameters.json may be used as follows:
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --parameter-file /tmp/sample_parameters.json
```

#### --request-file
Specifies a JSON file that contains the complete request i.e source, destination, tags and parameters.
See [Customizing Pipeline Requests](../docs/customizing_pipeline_requests.md) for examples of requests in JSON format.
> **Note**: As vaclient volume mounts /tmp, the request file may be placed there.

A sample request file can look like
```json
{
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
        "detection-device": "GPU"
    }
}
```
The above file, named for instance as /tmp/sample_request.json may be used as follows:
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike --request-file /tmp/sample_request.json
```

#### --tag
Specifies a key, value pair to update request with. This information is added to each frame's metadata.
This example adds tags for direction and location of video capture
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --tag direction east --tag camera_location parking_lot
```

#### --show-request
All vaclient commands can be used with the `--show-request` option which will print out the HTTP request and exit i.e it will not be sent to VA Serving.
This example shows the result of `--show-request` when the pipeline is started with options passed in
```
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --destination path /tmp/newfile.jsonl --parameter detection-device GPU --tag direction east --tag camera_location parking_lot --show-request
```
```
<snip>
POST http://localhost:8080/pipelines/object_detection/person_vehicle_bike
Body:{'source': {'uri': 'https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true', 'type': 'uri'}, 'destination': {'metadata': {'type': 'file', 'path': '/tmp/newfile.jsonl', 'format': 'json-lines'}}, 'parameters': {'detection-device': 'GPU'}, 'tags': {'direction': 'east', 'camera_location': 'parking_lot'}}
```
See [View REST request](../README.md#view-rest-request) to see how the output from `--show-request` can be mapped to a curl command.

### Status/Wait/Stop Arguments
This section summarizes all the arguments for vaclient `status`, `wait` and `stop` commands.

#### pipeline (required)
Positional argument (first) that specifies the pipeline to wait on/query status of/stop as indicated in the form of `pipeline name/pipeline version`

#### instance (required)
Positional argument (second) that specifies pipeline instance id to wait on/query status of/stop based on the command.

#### --show-request
As mentioned before, `--show-request` option which will print out the HTTP request and exit.

##### Status
```
./vaclient/vaclient.sh status object_detection/person_vehicle_bike 1 --show-request
```
```
<snip>
GET http://localhost:8080/pipelines/object_detection/person_vehicle_bike/1/status
```
##### Wait
```
./vaclient/vaclient.sh wait object_detection/person_vehicle_bike 1 --show-request
```
```
<snip>
GET http://localhost:8080/pipelines/object_detection/person_vehicle_bike/1/status
```
##### Stop
```
./vaclient/vaclient.sh stop object_detection/person_vehicle_bike 1 --show-request
```
```
<snip>
DELETE http://localhost:8080/pipelines/object_detection/person_vehicle_bike/1
```