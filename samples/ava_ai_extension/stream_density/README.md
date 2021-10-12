# Measuring Stream Density
Show how stream density can be increased with GPU accelerator and by DL Streamer's tracking feature.

The following results were obtained from a [NUC11TNKv7](https://www.intel.com/content/www/us/en/products/sku/205607/intel-nuc-11-pro-kit-nuc11tnkv7/specifications.html)
* Media: https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4
  * Must be copied locally to samples/ava_ai_extension/stream_density/people-detection.mp4
* Detection model: person-vehicle-bike-detection-crossroad-0078
* Stream density is number of concurrent streams processed 30fps

Stream density results [1](#notices-and-disclaimers):

|Configuration|Stream Density|
|-------------|--------------|
|CPU object detection|0 (27fps)|
|GPU object detection|3|
* GPU object detection accelerated with tracking/classification: stream density|9|

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
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-cpu.json --shared-memory -f file:///home/video-analytics-serving/samples/ava_ai_extension/stream_density/people-detection.mp4
<snip>
[AIXC] [2021-10-07 21:12:53,362] [MainThread  ] [INFO]: Client finished execution
```
Get fps from server.
```
Waiting for stream to start...
Test started 2021-10-12 22:34:42.737000
Stream 1 started.
Stream 1 ended, duration = 22s, fps = 27
Test finished: 0/1 streams pass, average fps = 27
```


## GPU Inference
Extension configuration is [detect-gpu.json](detect-gpu.json).

Now run three streams at once and measure fps
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu.json  --shared-memory -f file:///home/video-analytics-serving/samples/ava_ai_extension/stream_density/people-detection.mp4 --number-of-streams 3
Starting Client 1 Results to /tmp/result_client_1.jsonl, Output to: client_1.stdout.txt
Starting Client 2 Results to /tmp/result_client_2.jsonl, Output to: client_2.stdout.txt
Starting Client 3 Results to /tmp/result_client_3.jsonl, Output to: client_3.stdout.txt
waiting for clients to finish
```
Get fps from server
```
Test started 2021-10-12 22:41:46.530000
Stream 1 started.
Stream 2 started.
Stream 3 started.
Stream 1 ended, duration = 18s, fps = 33
Stream 2 ended, duration = 18s, fps = 33
Stream 3 ended, duration = 18s, fps = 33
Test finished: 3/3 streams pass, average fps = 33
```
All streams > 30fps => stream density = 3.

### GPU Inference + Tracking
Run inference on every 4th frame, rely on tracking to do detection in the interim.

Extension configuration is [detect-gpu-tracking.json](detect-gpu-tracking.json).

Run 12 streams at once and measure fps.
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu-tracking.json --shared-memory -f file:///home/video-analytics-serving/samples/ava_ai_extension/stream_density/people-detection.mp4 --number-of-streams 9
Starting Client 1 Results to /tmp/result_client_1.jsonl, Output to: client_1.stdout.txt
Starting Client 2 Results to /tmp/result_client_2.jsonl, Output to: client_2.stdout.txt
Starting Client 3 Results to /tmp/result_client_3.jsonl, Output to: client_3.stdout.txt
Starting Client 4 Results to /tmp/result_client_4.jsonl, Output to: client_4.stdout.txt
Starting Client 5 Results to /tmp/result_client_5.jsonl, Output to: client_5.stdout.txt
Starting Client 6 Results to /tmp/result_client_6.jsonl, Output to: client_6.stdout.txt
Starting Client 7 Results to /tmp/result_client_7.jsonl, Output to: client_7.stdout.txt
Starting Client 8 Results to /tmp/result_client_8.jsonl, Output to: client_8.stdout.txt
Starting Client 9 Results to /tmp/result_client_9.jsonl, Output to: client_9.stdout.txt
waiting for clients to finish
```
Stream density measurement is as follows
```
Test started 2021-10-12 22:51:28.445000
Stream 1 started.
Stream 2 started.
Stream 3 started.
Stream 4 started.
Stream 5 started.
Stream 6 started.
Stream 7 started.
Stream 8 started.
Stream 9 started.
Stream 1 ended, duration = 19s, fps = 31
Stream 2 ended, duration = 20s, fps = 30
Stream 3 ended, duration = 20s, fps = 30
Stream 4 ended, duration = 19s, fps = 31
Stream 5 ended, duration = 19s, fps = 32
Stream 6 ended, duration = 19s, fps = 32
Stream 7 ended, duration = 18s, fps = 33
Stream 8 ended, duration = 18s, fps = 33
Stream 9 ended, duration = 18s, fps = 34
Test finished: 9/9 streams pass, average fps = 32
```

## AVA Configuration

### Topology
Make sure shared memory is enabled.
```
        "extensionConfiguration": "${extensionConfiguration}",
          "dataTransfer": {
              "mode": "sharedMemory",
              "SharedMemorySizeMiB": "64"
        },
```

### Extension Configuration
We define pipeline request using the AVA extension configuration options. The standalone client uses JSON files mounted by the client through use of `--dev` mode.

For AVA operation the configuration is included in the operations file as escaped JSON. Use the script [json-escape.sh](json-escape.sh) that converts JSON files to an escaped string for inclusion in operations file.

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

## Notices and Disclaimers
Performance varies by use, configuration and other factors. Learn more at www.Intel.com/PerformanceIndex​​.

Performance results are based on testing as of dates shown in configurations and may not reflect all publicly available ​updates.  See backup for configuration details.  No product or component can be absolutely secure.

Your costs and results may vary.

Intel technologies may require enabled hardware, software or service activation.

© Intel Corporation.  Intel, the Intel logo, and other Intel marks are trademarks of Intel Corporation or its subsidiaries.  Other names and brands may be claimed as the property of others.  ​
