# Measuring Stream Density
Show how stream density can be increased with GPU accelerator and by DL Streamer's tracking feature.

The following results were obtained from a [NUC11TNKv7](https://www.intel.com/content/www/us/en/products/sku/205607/intel-nuc-11-pro-kit-nuc11tnkv7/specifications.html)
* Media: https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4.
* Detection model: person-vehicle-bike-detection-crossroad-0078

* CPU object detection: stream density = 0
* GPU object detection: stream density = 3
* GPU object detection accelerated with tracking/classification: stream density = 12

## Server Configuration
If host is Ubuntu 20 get the platform specific render group id required for GPU access.
```
$ stat -c "%g" /dev/dri/render*
109
```
Docker run command line - this contains the information necessary for AVA deployment file.
```
docker run -it --rm -v /dev/shm:/dev/shm --device /dev/dri -p 5001:5001 --name dlstreamer-edge-ai-extension --user $UID --group-add 109 --group-add users intel/video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension
```

GPU driver will self-configure on the first run causing a 30s delay, so use single frame to warm the pipeline.
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu.json
<30s wait>
<snip>
[AIXC] [2021-10-12 21:58:31,654] [MainThread  ] [INFO]: Start Time: 1634075891.8440084 End Time: 1634075911.6543307 Frames: Tx 1 Rx 1 FPS: 0.05047873455205729
[AIXC] [2021-10-12 21:58:31,656] [MainThread  ] [INFO]: Client finished execution
```

## Stream Density Measurements
Measurements were made using "standalone " mode (i.e. a local standalone client that support's AVA gRPC extension protocol).


## Measuring Stream Density
Fps is reported by the server at end of stream so can be determined by analyzing the log file. See example shown below.
```
{"levelname": "INFO", "asctime": "2021-10-08 04:07:51,980", "message": "Pipeline Ended Status: PipelineStatus(avg_fps=35.00980363501508, avg_pipeline_latency=None, elapsed_time=17.023804664611816, id=33, start_time=1633666054.9419162, state=<State.COMPLETED: 3>)", "module": "media_graph_extension"}
```

The [monitor_stream_density.sh](monitor_stream_density.sh) does this for you.
It assumes docker image name is `dlstreamer-edge-ai-extension`. It is different, simply edit script and re-run.

Start container then run script in it's own terminal window and
output will look like this for a test with four streams. If all stream pass, a stream density of 4 has been achieved. You can run more tests without having to re-start script.
```
$ ./monitor_stream_density.sh
Waiting for stream to start...
Test started 2021-10-09 07:01:02,738
Stream 1 started
Stream 2 started
Stream 3 started
Stream 4 started
Stream 1 ended, fps = 38
Stream 2 ended, fps = 38
Stream 3 ended, fps = 38
Stream 4 ended, fps = 39
Test finished: 4/4 streams pass, average fps = 38
```

A failed test will look like this.
```
Waiting for stream to start...
Test started 2021-10-11 06:30:59,503
Stream 1 started
Stream 2 started
Stream 3 started
Stream 4 started
Stream 5 started
Stream 6 started
Stream 1 ended, fps = 26
Stream 2 ended, fps = 25
Stream 3 ended, fps = 25
Stream 4 ended, fps = 26
Stream 5 ended, fps = 26
Stream 6 ended, fps = 26
Test finished: 0/6 streams pass, average fps = 26
Waiting for stream to start...
```


### CPU Inference
Extension configuration is [detect-cpu.json](detect-cpu.json).
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-cpu.json --shared-memory -f https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=true
<snip>
[AIXC] [2021-10-07 21:12:53,362] [MainThread  ] [INFO]: Client finished execution
```
Get fps from server.
```
```
We get 27.9fps - we're assuming close enough to 30fps to map to stream density of 1.

## GPU Inference
Extension configuration is [detect-gpu.json](detect-gpu.json).

Now run three streams at once and measure fps
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu.json  --shared-memory -f https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=true --number-of-streams 3
Starting Client 1 Results to /tmp/result_client_1.jsonl, Output to: client_1.stdout.txt
Starting Client 2 Results to /tmp/result_client_2.jsonl, Output to: client_2.stdout.txt
Starting Client 3 Results to /tmp/result_client_3.jsonl, Output to: client_3.stdout.txt
waiting for clients to finish
```
Get fps from server
```
$ docker logs dlstreamer-edge-ai-extension | grep avg_fps | tail -3
{"levelname": "INFO", "asctime": "2021-10-08 04:07:51,980", "message": "Pipeline Ended Status: PipelineStatus(avg_fps=35.00980363501508, avg_pipeline_latency=None, elapsed_time=17.023804664611816, id=33, start_time=1633666054.9419162, state=<State.COMPLETED: 3>)", "module": "media_graph_extension"}
{"levelname": "INFO", "asctime": "2021-10-08 04:07:53,205", "message": "Pipeline Ended Status: PipelineStatus(avg_fps=34.81964614019493, avg_pipeline_latency=None, elapsed_time=17.116775512695312, id=34, start_time=1633666056.0737617, state=<State.COMPLETED: 3>)", "module": "media_graph_extension"}
{"levelname": "INFO", "asctime": "2021-10-08 04:07:54,099", "message": "Pipeline Ended Status: PipelineStatus(avg_fps=35.86024580527947, avg_pipeline_latency=None, elapsed_time=16.62007784843445, id=35, start_time=1633666057.479542, state=<State.COMPLETED: 3>)", "module": "media_graph_extension"}
```
All streams > 30fps => stream density = 3.

> With number-of-streams = 4 we get ~28fps per stream.

### GPU Inference + Tracking
Run inference on every 4th frame, rely on tracking to do detection in the interim.

Extension configuration is [detect-gpu-tracking.json](detect-gpu-tracking.json).

Run 12 streams at once and measure fps.
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu-tracking.json --shared-memory -f https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=true --number-of-streams 12
Starting Client 1 Results to /tmp/result_client_1.jsonl, Output to: client_1.stdout.txt
Starting Client 2 Results to /tmp/result_client_2.jsonl, Output to: client_2.stdout.txt
Starting Client 3 Results to /tmp/result_client_3.jsonl, Output to: client_3.stdout.txt
Starting Client 4 Results to /tmp/result_client_4.jsonl, Output to: client_4.stdout.txt
Starting Client 5 Results to /tmp/result_client_5.jsonl, Output to: client_5.stdout.txt
Starting Client 6 Results to /tmp/result_client_6.jsonl, Output to: client_6.stdout.txt
Starting Client 7 Results to /tmp/result_client_7.jsonl, Output to: client_7.stdout.txt
Starting Client 8 Results to /tmp/result_client_8.jsonl, Output to: client_8.stdout.txt
Starting Client 9 Results to /tmp/result_client_9.jsonl, Output to: client_9.stdout.txt
Starting Client 10 Results to /tmp/result_client_10.jsonl, Output to: client_10.stdout.txt
Starting Client 11 Results to /tmp/result_client_11.jsonl, Output to: client_11.stdout.txt
Starting Client 12 Results to /tmp/result_client_12.jsonl, Output to: client_12.stdout.txt
waiting for clients to finish
```
Stream density measurement is as follows
```
```

## AVA Configuration

### Extension Configuration
We define pipeline request using the AVA extension configuration options. The standalone client uses JSON files mounted by the client through use of `--dev` mode.

For "end-to-end" operation the configuration is included in the operations file as escaped JSON. We created a script [json-escape.sh](json-escape.sh) that converts JSON files to an escaped string for inclusion in operations file.

As an example

```
$ ./json-escape.sh detect-cpu.json
"{\"pipeline\":{\"name\":\"object_detection\",\"version\":\"person_vehicle_bike_detection\"}}"
```
Then in operations file define as follows
```
{
    "name": "extensionConfiguration",
    "value": "{\"pipeline\":{\"name\":\"object_detection\",\"version\":\"person_vehicle_bike_detection\"}}"
}
```
