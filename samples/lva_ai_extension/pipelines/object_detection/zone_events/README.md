## Extension Configuration - Spatial Analytics

### Zone Detection

The `object_detection/zone_events` pipeline demonstrates how to integrate LVA with Spatial Analytics. The calling application may define one or more polygon regions as extension configuration.

When objects are detected as input that `intersect` the zone or are/become contained `within` a zone, along with the inference entity LVA emits a region event.

By setting `enable_watermark` the caller may visualize by modifying the pipeline to use fpsdisplaysink and gvawatermark elements, or add a `frame-destination` parameter for RTSP output.

#### Build and Run

1. Build:

   ```
   $ ./samples/lva_ai_extension/build.sh
   ```

2. Run server:

   ```
   $ ./samples/lva_ai_extension/run_server.sh
   ```

3. Run client with example extension configuration:

   ```
   $ ./samples/lva_ai_extension/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/zones-spatial-analytics.json
   ```

#### Expected Spatial Analytics Output


The primary workflow is driven by `zones-spatial-analytics.json` which contains the minimal required configuration to produce zone events for a media stream.

```
<snip>
[AIXC] [INFO]: Inference result 504
[AIXC] [INFO]: ENTITY - person (0.98) [0.10, 0.08, 0.06, 0.17] ['inferenceId: eb3bb2d8f91348c68db4886f5fe568e9']
[AIXC] [INFO]: EVENT - zone_event: ["relatedInferences: ['eb3bb2d8f91348c68db4886f5fe568e9']", 'status: intersects', 'zone: Zone1']
[AIXC] [INFO]: EVENT - zone_event: ["relatedInferences: ['eb3bb2d8f91348c68db4886f5fe568e9']", 'status: intersects', 'zone: Zone2']
[AIXC] [INFO]: Inference result 505
[AIXC] [INFO]: ENTITY - person (0.98) [0.11, 0.08, 0.05, 0.18] ['inferenceId: 53e6602820e54476b5b360c46ee90014']
[AIXC] [INFO]: EVENT - zone_event: ["relatedInferences: ['53e6602820e54476b5b360c46ee90014']", 'status: intersects', 'zone: Zone1']
[AIXC] [INFO]: EVENT - zone_event: ["relatedInferences: ['53e6602820e54476b5b360c46ee90014']", 'status: intersects', 'zone: Zone2']
```

#### VA Serving Rendered Pipeline

Adding a configuration parameter to specify the frame-destination enables a secondary workflow, with VA Serving rendering visualization of regions and entity detections/events (shown below).

This added to the `zones-vaserving-rendered.json` extension configuration. So following the same instructions above but swapping the extension configuration used will dynamically produce the scene using rudimentary markers/dots showing the boundary of the defined polygon regions. This allows the DL Streamer `gvawatermark` element (used in the frame-destination) to handle rendering.

> gvawatermark does not draw the polygon lines, so the view must currently "connect the dots" themself.

  We add a label when a detection entity intersects or is within a defined region.

1. Run server:

   ```
   $ ENABLE_RTSP=true ./samples/lva_ai_extension/run_server.sh
   ```

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./samples/lva_ai_extension/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/zones-vaserving-rendered.json
   ```


#### Troubleshooting

   1. Run with DEV mode to volume mount local LVA paths. This is useful when iterating on local scripts and related configurations since you can modify and run them without rebuilding these into the Docker image.

   ```
   $ unset ENABLE_RTSP && ./samples/lva_ai_extension/docker/run_server.sh --dev
   ```

   2. Override runtime parameters such as `--sample-file-path` to modify the default video source content. Ex:

   ```
   samples/lva_ai_extension/docker/run_client.sh --dev \
    --extension-config /home/video-analytics-serving/samples/lva_ai_extension/ai_skills/region_detection/spatial-analytics.json \
    --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
   ```
   3. Update log levels:

      - Update extension configuration to pass `"log_level":"DEBUG"`. This produces verbose messages that originate from the zone_events callback.
      - Update GST_DEBUG log levels via environment variable. Ex: `GST_DEBUG=gvadetect:6`
      - Update additional VA Serving log levels.

