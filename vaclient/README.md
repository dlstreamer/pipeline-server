# Using Video Analytics Serving Sample Client
These steps walk you through how to launch the sample client that is included in the repository to exercise the VA Serving REST-API.

## Build the image
Build the container which includes the service and client:
```
~/video-analytics-serving$ ./docker/build.sh
```

## Start the service
Run the container with the temp folder volume mounted to capture results.
```
~/video-analytics-serving$ ./docker/run.sh -v /tmp:/tmp --name vaserving
```

## Running the client
Start a new shell

### Running Pipelines
vaclient can be used to send pipeline start requests using the `run` command. With the `run` command you will need to enter two additional arguments the `pipeline` (in the form of pipeline_name/pipeline_version) you wish to use and the `uri` pointing to the media of your choice.
```
./vaclient/vaclient.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
As the pipeline runs, the output file is processed by vaclient and inference information is printed to the screen in the following format: `label (confidence) [t l w h] {meta-data}` At the end of the pipeline run, the average fps is printed as well. If you wish to stop the pipeline mid-run, `Ctrl+C` will signal the client to send a `stop` command to the service. Once the pipeline is stopped, vaclient will output the average fps. More on `stop` below

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
./vaclient/vaclient.sh start object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
```
#### Instance ID
On a successful start of a pipeline, vaserving assigns a pipeline `instance_id` which is a unique number which can be used to reference the pipeline in subsequent requests. In this example, the `instance_id` is `1`
```
Starting pipeline...
Pipeline running
Pipeline instance = object_detection/person_vehicle_bike/1
```
### Stopping Pipelines
If you want to stop a pipeline

#### Explore running new pipelines, passing other sources, destination targets, and other options described in the help function:


### Clean up
Remember to stop the service container once finished
```
	 # docker kill vaserving
```
