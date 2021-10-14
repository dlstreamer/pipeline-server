# Measuring Stream Density with DL Streamer AI Extension

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

## Measuring Stream Density
Fps is reported by the server at end of stream so can be determined by analyzing the log file. See example shown below.
```
{"levelname": "INFO", "asctime": "2021-10-08 04:07:51,980", "message": "Pipeline Ended Status: PipelineStatus(avg_fps=35.00980363501508, avg_pipeline_latency=None, elapsed_time=17.023804664611816, id=33, start_time=1633666054.9419162, state=<State.COMPLETED: 3>)", "module": "media_graph_extension"}
```

The [monitor_stream_density.sh](monitor_stream_density.sh) does this for you.
It assumes docker image name is `dlstreamer-edge-ai-extension`. It is different, simply edit script and re-run.

Start container then run script in it's own terminal window and output will look like this for a test with four streams. 
If all stream pass, a stream density of 4 has been achieved. You can run more tests without having to re-start script.

Here's an example of running 4 streams.

First issue requests.
```
$ samples/ava_ai_extension/docker/run_client.sh --dev --extension-config /home/video-analytics-serving/samples/ava_ai_extension/stream_density/detect-gpu-tracking.json --shared-memory -f file:///home/video-analytics-serving/samples/ava_ai_extension/stream_density/people-detection.mp4 --number-of-streams 4
```
Then in a different window, run monitor tool.
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

A failed test with 6 streams will look like this.
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

## Example Extension Configurations
* CPU Inference: [detect-cpu.json](detect-cpu.json)
* GPU Inference: [detect-gpu.json](detect-gpu.json)
* GPU Inference + Tracking: [detect-gpu-tracking.json](detect-gpu-tracking.json) 

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

