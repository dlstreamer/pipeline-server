## Extension Configuration - Spatial Analytics

### Line Crossing  Events

The `object_tracking/line_crossing` pipeline demonstrates how to integrate LVA with Spatial Analytics. The calling application may define one or more lines in extension configuration.

When objects are detected as input that crosses a line, along with the inference entity LVA emits a `lineCrossing` event.


#### Build and Run

1. Build:

   ```
   $ ./samples/lva_ai_extension/docker/build.sh
   ```

2. Run server:

   ```
   $ ./samples/lva_ai_extension/docker/run_server.sh
   ```

3. Run client with example extension configuration:

   ```
   $ ./samples/lva_ai_extension/docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/line_cross_tracking_config.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=True
   ```

#### Expected Spatial Analytics Output

The primary workflow is driven by `line_cross_tracking_config.json` which contains the minimal required configuration to produce `lineCrossing` events for a media stream.

```
<snip>
[AIXC] [2021-05-12 18:57:01,315] [MainThread  ] [INFO]: ENTITY - person (1.00) [0.40, 0.27, 0.12, 0.62] ['inferenceId: d47a4192ca4b4933a6c6c588220f59de', 'subtype: objectDetection', 'id: 1']
[AIXC] [2021-05-12 18:57:01,315] [MainThread  ] [INFO]: EVENT - hallway_bottom: ['inferenceId: 520d7506e5c94f3b9aeb1d157af6311c', 'subtype: lineCrossing', "relatedInferences: ['d47a4192ca4b4933a6c6c588220f59de']", 'counterclockwiseTotal: 1', 'total: 1', 'clockwiseTotal: 0', 'direction: counterclockwise']
```

#### VA Serving Rendered Pipeline

Adding a configuration parameter to specify the frame-destination enables a secondary workflow, with VA Serving rendering visualization of lines and entity detections/events (shown below).

By setting `enable_watermark` and `frame-destination` parameter for RTSP re streaming, the caller may visualize the output. This added to the `line_cross_tracking_config_rtsp.json` extension configuration. So following the same instructions above but swapping the extension configuration used will dynamically produce the scene using rudimentary markers/dots showing the start and end points of defined lines. This allows the DL Streamer `gvawatermark` element (used in the frame-destination) to handle rendering.

> gvawatermark does not draw the lines, so the view must currently "connect the dots" themself.

1. Run server:

   ```
   $ ENABLE_RTSP=true ./samples/lva_ai_extension/docker/run_server.sh
   ```

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./samples/lva_ai_extension/docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/line_cross_tracking_config_rtsp.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=True
   ```

3. Connect and visualize: Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/vaserving`.