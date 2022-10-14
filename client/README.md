# Pipeline Client Command Reference
pipeline_client is a python app intended to be a reference for using Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server REST API. pipeline_client is included in Pipeline Server's REST container and can be easily launched using the accompanying run script, `pipeline_client.sh`.

>**Note:**
This document assumes you are familiar with Intel(R) DL Streamer Pipeline Server and have built the image locally and Pipeline Server REST instance is running for Pipeline Client to connect to. See the main [README](../README.md) for details on building and running the service.

## Basic Usage
### Listing Supported Models and Pipelines
To see which models and pipelines are loaded by the service run the following commands.
> **Note:** Results will vary depending on your service configuration but the format of models and pipelines are displayed in the tuplet form of name/version as seen below.

Listing models:
```
 ./client/pipeline_client.sh list-models
```
```
<snip>
 - object_classification/vehicle_attributes
 - emotion_recognition/1
 - audio_detection/environment
 - object_detection/person_vehicle_bike
 - face_detection_retail/1
```

Listing pipelines:
```
./client/pipeline_client.sh list-pipelines
```
```
<snip>
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - object_tracking/person_vehicle_bike
 - object_tracking/object_line_crossing
 - object_detection/person_vehicle_bike
 - object_detection/object_zone_count
```

### Running Pipelines
pipeline_client can be used to send pipeline start requests using the `run` command. With the `run` command you will need to enter two additional arguments the `pipeline` (in the form of pipeline_name/pipeline_version) you wish to use and the `uri` pointing to the media of your choice.
```
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
If the pipeline request is successful, an instance id is created and pipeline_client will print the instance. More on `instance_id` below.
Once pre-roll is completed and pipeline begins running, the output file is processed by pipeline_client and inference information is printed to the screen in the following format: `label (confidence) [top left width height] {meta-data}` At the end of the pipeline run, the average fps is printed as well. If you wish to stop the pipeline mid-run, `Ctrl+C` will signal the client to send a `stop` command to the service. Once the pipeline is stopped, pipeline_client will output the average fps. More on `stop` below

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
However, if there are errors during pipeline execution i.e GPU is specified as detection device but is not present, pipeline_client will terminate with an error message
```
Pipeline instance = <uuid>
<Error Message>
```

### Starting Pipelines
The `run` command is helpful for quickly showing inference results but `run` blocks until completion. If you want to do your own processing and only want to kickoff a pipeline, this can be done with the `start` command. `start` arguments are the same as `run`, you'll need to provide the `pipeline` and `uri`. Run the following command:
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
Similar to `run`, if the pipeline request is successful, an instance id is created and pipeline_client will print the instance. More on `instance_id` below.
```
Pipeline instance = <uuid>
```
Errors during pipeline execution are not flagged as pipeline_client exits after receiving instance id for a successful request. However, both `start` and `run` will flag invalid requests, for example:
```
./client/pipeline_client.sh start object_detection/person_vehicle_bke https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
The pipeline name has a typo `object_detection/person_vehicle_bke` making it invalid, this results in the error message:
```
400 - "Invalid Pipeline or Version"
```

#### Instance ID
On a successful start of a pipeline, Pipeline Server assigns a pipeline `instance_id` which is a [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) which can be used to reference the pipeline in subsequent requests. In this example, the `instance_id` is `0fe8f408ea2441bca8161e1190eefc51`
```
Starting pipeline object_detection/person_vehicle_bike, instance = 0fe8f408ea2441bca8161e1190eefc51
```
### Stopping Pipelines
Stopping a pipeline can be accomplished using the `stop` command along with the `pipeline` and `instance id`:
```
./client/pipeline_client.sh stop object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
```
```
Stopping Pipeline...
Pipeline stopped
avg_fps: 42.07
```
### Getting Pipeline Status
Querying the current state of the pipeline is done using the `status` command along with the `pipeline` and `instance id`:
```
./client/pipeline_client.sh status object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
```
pipeline_client will print the status of `QUEUED`, `RUNNING`, `ABORTED`, `COMPLETED`  along with the fps or `ERROR` with the error message as applicable.
```
<snip>
RUNNING (30fps)
```
```
<snip>
ERROR (Not Found (404), URL: https://github.com/intel-iot-devkit/sample.mp4, Redirect to: (NULL))
```

### Waiting for a pipeline to finish
If you wish to wait for a pipeline to finish running you can use the `wait` command along with the `pipeline` and `instance id`:
```
./client/pipeline_client.sh wait object_detection/person_vehicle_bike 0fe8f408ea2441bca8161e1190eefc51
```
The client will print the initial status of the pipeline. Then wait for completion and print the average fps.

### Getting Status of All Pipelines
Querying the current state of the pipeline is done using the `list-instances` command.

This example starts two pipelines and then gets their status and request details.
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
Output:
```
Starting pipeline object_detection/person_vehicle_bike, instance = 94cf72b718184615bfc181c6589b240c
```
```
./client/pipeline_client.sh start object_classification/vehicle_attributes https://github.com/intel-iot-devkit/sample-videos/blob/master/car-detection.mp4?raw=true
```
Output:
```
Starting pipeline object_classification/vehicle_attributes, instance = 978e09c561f14fa1b793e8b644f30031
```
```
./client/pipeline_client.sh list-instances
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
This optional argument is meant to handle logging verbosity common across all commands to pipeline_client.
> **Note**: If specified, --quiet needs to be placed ahead of the specific command i.e start, run etc.

#### Start
pipeline_client output will just be the pipeline instance.
```
./client/pipeline_client.sh --quiet start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
```
<snip>
280ff2c4a54611ec8b900242ac110002
```
#### Run
pipeline_client output will be the pipeline instance followed by inference results.
```
./client/pipeline_client.sh --quiet run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
```
<snip>
280ff2c4a54611ec8b900242ac110002
Timestamp 1500000000
- person (0.54) [0.67, 0.88, 0.74, 1.00]
Timestamp 1666666666
- person (0.55) [0.68, 0.83, 0.74, 1.00]
```

### Run/Start Arguments
This section summarizes all the arguments for pipeline_client `run` and `start` commands.

#### pipeline (required)
Positional argument (first) that specifies the pipeline to be launched in the form of `pipeline name/pipeline version`.

#### uri (optional)
Positional argument (second) that specifies the location of the content to play/analyze.
> Note: uri argument can be skipped only if passed in via --request-file

#### --destination
By default, pipeline_client uses a generic template for destination:
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
> **Note**: You may need to volume mount this new location when running Pipeline Server.
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --destination path /tmp/newfile.jsonl
```

If other destination types are specified (e.g. `mqtt` or `kafka` ), the pipeline will try to publish to specified broker and pipeline_client will subscribe to it and display published metadata. Here is an mqtt example using a broker on localhost.
```
docker run --rm --network=host -d eclipse-mosquitto:1.6
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --destination type mqtt --destination host localhost:1883 --destination topic pipeline-server
```
```
Starting pipeline object_detection/person_vehicle_bike, instance = <uuid>
Pipeline running - instance_id = <uuid>
Timestamp 3666666666
- person (0.91) [0.75, 0.50, 0.81, 0.70]
Timestamp 3750000000
- person (0.91) [0.76, 0.50, 0.81, 0.68]
Timestamp 3833333333
- person (0.82) [0.76, 0.49, 0.82, 0.69]
Timestamp 3916666666
- person (0.70) [0.76, 0.48, 0.82, 0.69]
Timestamp 4000000000
- person (0.59) [0.76, 0.47, 0.83, 0.69]
```
For more details on destination types, see [customizing pipeline requests](../docs/customizing_pipeline_requests.md#metadata).
#### --rtsp-path
If you are utilizing RTSP restreaming, `--rtsp-path` can be used to update the `server_url` path. This updates the frame part of destination under the hood.
For example, adding `--rtsp-path new_path` will able you to view the stream at `rtsp://<ip_address>:<port>/new_path`. More details on RTSP restreaming in [running_pipeline_server](../docs/running_pipeline_server.md) documentation.

#### --parameter
By default, pipeline_client relies on pipeline parameter defaults. This can be updated with `--parameter` option. See [Defining Pipelines](../docs/defining_pipelines.md) to know how parameters are defined. The following example adds `--parameter detection-device GPU`
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --parameter detection-device GPU
```

#### --parameter-file
Specifies a JSON file that contains parameters in key, value pairs. Parameters from this file take precedence over those set by `--parameter`.
> **Note**: As pipeline_client volume mounts /tmp, the parameter file may be placed there.

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
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --parameter-file /tmp/sample_parameters.json
```

#### --tag
Specifies a key, value pair to update request with. This information is added to each frame's metadata.
This example adds tags for direction and location of video capture
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --tag direction east --tag camera_location parking_lot
```

#### --server-address
This can be used with any command to specify a remote HTTP server address. Here we start a pipeline on remote server `http://remote-server.my-domain.com:8080`.

```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --tag direction east --server-address http://remote-server.my-domain.com:8080
```

#### --status-only
Use with `run` command to disable output of metadata and periodically display pipeline state and fps
```
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --tag direction east --status-only
```
```
Starting pipeline 0
Starting pipeline object_detection/person_vehicle_bike, instance = <uuid>
Pipeline 0 running - instance_id = <uuid>
Pipeline status @ 6s
- instance=<uuid>, state=RUNNING, 24fps
Pipeline status @ 11s
- instance=<uuid>, state=RUNNING, 21fps
Pipeline status @ 16s
- instance=<uuid>, state=RUNNING, 21fps
Pipeline status @ 21s
- instance=<uuid>, state=RUNNING, 20fps
```

#### --number-of-streams
Takes an integer value that specifies the number of streams to start (default value is 1) using specified request.
If number of streams is greater than one, "status only" display mode is used.
```
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --status-only --number-of-streams 4 --server-address http://hbruce-desk2.jf.intel.com:8080
```
```
Starting pipeline 0
Starting pipeline object_detection/person_vehicle_bike, instance = <uuid>
Pipeline 0 running - instance_id = <uuid>
Starting pipeline 1
Starting pipeline object_detection/person_vehicle_bike, instance = f20d1e60806311ecad1c3417ebbc7e7a
Pipeline 1 running - instance_id = f20d1e60806311ecad1c3417ebbc7e7a
Starting pipeline 2
Starting pipeline object_detection/person_vehicle_bike, instance = f2faeb04806311ecad1c3417ebbc7e7a
Pipeline 2 running - instance_id = f2faeb04806311ecad1c3417ebbc7e7a
Starting pipeline 3
Starting pipeline object_detection/person_vehicle_bike, instance = f435a0fe806311ecad1c3417ebbc7e7a
Pipeline 3 running - instance_id = f435a0fe806311ecad1c3417ebbc7e7a
All 4 pipelines running.
Pipeline status @ 11s
- instance=<uuid>, state=RUNNING, 20fps
- instance=f20d1e60806311ecad1c3417ebbc7e7a, state=RUNNING, 15fps
- instance=f2faeb04806311ecad1c3417ebbc7e7a, state=RUNNING, 13fps
- instance=f435a0fe806311ecad1c3417ebbc7e7a, state=RUNNING, 12fps
Pipeline status @ 16s
- instance=<uuid>, state=RUNNING, 17fps
- instance=f20d1e60806311ecad1c3417ebbc7e7a, state=RUNNING, 14fps
- instance=f2faeb04806311ecad1c3417ebbc7e7a, state=RUNNING, 12fps
- instance=f435a0fe806311ecad1c3417ebbc7e7a, state=RUNNING, 12fps
Pipeline status @ 21s
- instance=<uuid>, state=RUNNING, 16fps
- instance=f20d1e60806311ecad1c3417ebbc7e7a, state=RUNNING, 13fps
- instance=f2faeb04806311ecad1c3417ebbc7e7a, state=RUNNING, 12fps
- instance=f435a0fe806311ecad1c3417ebbc7e7a, state=RUNNING, 12fps
```

#### --request-file
Specifies a JSON file that contains the complete request i.e source, destination, tags and parameters.
See [Customizing Pipeline Requests](../docs/customizing_pipeline_requests.md) for examples of requests in JSON format.
> **Note**: As pipeline_client volume mounts /tmp, the request file may be placed there.

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
./client/pipeline_client.sh start object_detection/person_vehicle_bike --request-file /tmp/sample_request.json
```

#### --show-request
All pipeline_client commands can be used with the `--show-request` option which will print out the HTTP request and exit i.e it will not be sent to the Pipeline Server.
This example shows the result of `--show-request` when the pipeline is started with options passed in
```
./client/pipeline_client.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true --destination path /tmp/newfile.jsonl --parameter detection-device GPU --tag direction east --tag camera_location parking_lot --show-request
```
```
<snip>
POST http://localhost:8080/pipelines/object_detection/person_vehicle_bike
Body:{'source': {'uri': 'https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true', 'type': 'uri'}, 'destination': {'metadata': {'type': 'file', 'path': '/tmp/newfile.jsonl', 'format': 'json-lines'}}, 'parameters': {'detection-device': 'GPU'}, 'tags': {'direction': 'east', 'camera_location': 'parking_lot'}}
```
See [View REST request](../README.md#view-rest-request) to see how the output from `--show-request` can be mapped to a curl command.

### Status/Wait/Stop Arguments
This section summarizes all the arguments for pipeline_client `status`, `wait` and `stop` commands.

#### pipeline (required)
Positional argument (first) that specifies the pipeline to wait on/query status of/stop as indicated in the form of `pipeline name/pipeline version`

#### instance (required)
Positional argument (second) that specifies pipeline instance id to wait on/query status of/stop based on the command.

#### --show-request
As mentioned before, `--show-request` option which will print out the HTTP request and exit.

##### Status
```
./client/pipeline_client.sh status object_detection/person_vehicle_bike 94cf72b718184615bfc181c6589b240c --show-request
```
```
<snip>
GET http://localhost:8080/pipelines/object_detection/person_vehicle_bike/status/94cf72b718184615bfc181c6589b240c
```
##### Wait
```
./client/pipeline_client.sh wait object_detection/person_vehicle_bike 94cf72b718184615bfc181c6589b240c --show-request
```
```
<snip>
GET http://localhost:8080/pipelines/object_detection/person_vehicle_bike/status/94cf72b718184615bfc181c6589b240c
```
##### Stop
```
./client/pipeline_client.sh stop object_detection/person_vehicle_bike 94cf72b718184615bfc181c6589b240c --show-request
```
```
<snip>
DELETE http://localhost:8080/pipelines/object_detection/person_vehicle_bike/94cf72b718184615bfc181c6589b240c
```

### Using HTTPS with Pipeline Client

To use Pipeline Client together with HTTPS, the request must provide `--server-address` with a https address and `--server-cert` with the server certificate as a configuration option to configure the client with the server certificate. This is handled by `pipeline-client.sh` and is set as an Environment variable to `pipeline_client.py`. Below is an example:

#### --server-cert
Specifies a certificate for HTTPS. This information is added to each request to run on HTTPS with the given certificate.
This example makes pipeline_client.sh use HTTPS by setting `--server-address` and `--server-cert`

This adds an Environment variable `ENV_CERT` and `REQUESTS_CA_BUNDLE` to accomodate for self-signed certificates. These environment variables can be ignored if you are not using self-signed certificate.

```sh
$ client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4\?raw\=true --server-address https://localhost:8443 --server-cert samples/nginx/cert/server.crt

.
.
.

Starting pipeline object_detection/person_vehicle_bike, instance = 1843e91040da11edbaf2b62e8c582e09
Pipeline running - instance_id = 1843e91040da11edbaf2b62e8c582e09
No results will be displayed. Unable to read from file /tmp/results.jsonl
avg_fps: 593.75
Done
```

### Working with Kubernetes

As Kubernetes deploys its' own MQTT broker inside the cluster, Pipeline Client requires a configuration to be set to `pipeline_client.sh`. This is handled by `pipeline_client.sh` and this configuration option is set as an Environment variable to `pipeline_client.py` to override MQTT broker's address for Kubernetes use case.

#### --mqtt-cluster-broker
This argument is to be used together with MQTT destination. This argument is helpful when your MQTT broker & Pipeline Server instance is on a separate network from your client machine. This happens in the Kubernetes deployment. Use this argument to set the client to connect to the MQTT broker directly to get the output. This will set an Environment variable `MQTT_CLUSTER_BROKER` which will override the existing MQTT broker destination for the client to connect.

```
./client/pipeline_client.sh run object_detection/person_vehicle_bike \
  https://lvamedia.blob.core.windows.net/public/homes_00425.mkv \
  --server-address http://remote-server.my-domain.com:8080 \
  --destination type mqtt --destination host mqtt-broker-address:1883 \
  --destination topic person-vehicle-bike \
  --mqtt-cluster-broker cluster-mqtt-broker-address:1883
```