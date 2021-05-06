## Extension Configuration - Spatial Analytics

### Zone Detection

The `object_detection/zone_events` pipeline demonstrates how to integrate LVA with Spatial Analytics. The calling application may define one or more polygon regions as extension configuration.

When objects are detected as input that `intersect` the zone or are/become contained `within` a zone, along with the inference entity LVA emits a region event.

By setting `enable_watermark` the caller may visualize by modifying the pipeline to use fpsdisplaysink and gvawatermark elements, or add a `frame-destination` parameter for RTSP output.

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
   $ ./samples/lva_ai_extension/docker/run_client.sh  --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/zones-spatial-analytics.json
   ```

#### Expected Spatial Analytics Output


The primary workflow is driven by `zones-spatial-analytics.json` which contains the minimal required configuration to produce zone events for a media stream.

```
<snip>
[AIXC] [2021-05-06 18:07:42,838] [MainThread  ] [INFO]: ENTITY - person (1.00) [0.30, 0.47, 0.09, 0.39] ['inferenceId: e3dd3b8152164036ab7ff38b47cee046']
[AIXC] [2021-05-06 18:07:42,838] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['e3dd3b8152164036ab7ff38b47cee046']", 'status: intersects']
[AIXC] [2021-05-06 18:07:42,838] [MainThread  ] [INFO]: ENTITY - person (0.97) [0.36, 0.40, 0.05, 0.24] ['inferenceId: 10352472d41246c5bc4c51a217056fd0']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['10352472d41246c5bc4c51a217056fd0']", 'status: intersects']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.94) [0.44, 0.42, 0.08, 0.43] ['inferenceId: 49da7b1cfefb4c77bd584f48e31aaed9']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['49da7b1cfefb4c77bd584f48e31aaed9']", 'status: intersects']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.92) [0.57, 0.38, 0.05, 0.25] ['inferenceId: cbaa54c9a13043fa914d37b0fc485f8c']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['cbaa54c9a13043fa914d37b0fc485f8c']", 'status: within']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.91) [0.69, 0.56, 0.12, 0.43] ['inferenceId: b6f3c7607f324a08880d231ba7ddd017']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['b6f3c7607f324a08880d231ba7ddd017']", 'status: intersects']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.90) [0.68, 0.42, 0.04, 0.24] ['inferenceId: 22ff47948fed49dbac5e1e4f5242552c']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['22ff47948fed49dbac5e1e4f5242552c']", 'status: within']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.82) [0.64, 0.36, 0.05, 0.27] ['inferenceId: 84f38536d9654ec9a5e0535747bbf020']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['84f38536d9654ec9a5e0535747bbf020']", 'status: within']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: ENTITY - person (0.60) [0.84, 0.44, 0.05, 0.29] ['inferenceId: d40b8e03135c4266bf069f4f515ed536']
[AIXC] [2021-05-06 18:07:42,839] [MainThread  ] [INFO]: EVENT - zone_event: ["relatedInferences: ['d40b8e03135c4266bf069f4f515ed536']", 'status: intersects']
```

#### VA Serving Rendered Pipeline

Adding a configuration parameter to specify the frame-destination enables a secondary workflow, with VA Serving rendering visualization of regions and entity detections/events (shown below).

This added to the `zones-spatial-analytics-rendered.json` extension configuration. So following the same instructions above but swapping the extension configuration used will dynamically produce the scene using rudimentary markers/dots showing the boundary of the defined polygon regions. This allows the DL Streamer `gvawatermark` element (used in the frame-destination) to handle rendering.

> gvawatermark does not draw the polygon lines, so the view must currently "connect the dots" themself.

  We add a label when a detection entity intersects or is within a defined region.

1. Run server:

   ```
   $ ENABLE_RTSP=true ./samples/lva_ai_extension/docker/run_server.sh
   ```

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./samples/lva_ai_extension/docker/run_client.sh \
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
