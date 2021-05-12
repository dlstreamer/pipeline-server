## Extension Configuration - Spatial Analytics

### Zone Detection

The `object_detection/zone_events` pipeline demonstrates how to integrate LVA with Spatial Analytics. The calling application may define one or more polygon regions as extension configuration.

When objects are detected as input that `intersect` the zone or are/become contained `within` a zone, LVA counts number of objects and emits `zoneCrossing` event.
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
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/zones-spatial-analytics.json
   ```

#### Expected Spatial Analytics Output

The primary workflow is driven by `zones-spatial-analytics.json` which contains the minimal required configuration to produce  `zoneCrossing` events for a media stream.

```
<snip>
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (1.00) [0.30, 0.47, 0.09, 0.39] ['inferenceId: c8f074e8575d4266a6010d5ed0ea6daf', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.97) [0.36, 0.40, 0.05, 0.24] ['inferenceId: 34cd8129edc34bfe8c96c49600a251df', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.94) [0.44, 0.42, 0.08, 0.43] ['inferenceId: a1e278d7b68d4eefbfbff35e80086a94', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.92) [0.57, 0.38, 0.05, 0.25] ['inferenceId: 697329a697694649aff3f25703bf9b16', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.91) [0.69, 0.56, 0.12, 0.43] ['inferenceId: 8e9323d8ed264b648887ede89767b830', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.90) [0.68, 0.42, 0.04, 0.24] ['inferenceId: 40f8d54d302b4438845046b991de48ee', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.82) [0.64, 0.36, 0.05, 0.27] ['inferenceId: fd2c302794184209b58c6b922ae1ae8c', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: ENTITY - person (0.60) [0.84, 0.44, 0.05, 0.29] ['inferenceId: e3e9f520defd4642a09f2bf702ec23f4', 'subtype: objectDetection']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: EVENT - Zone2: ['inferenceId: 7a9adc6a29dd48eeae83b3fadc1719af', 'subtype: zoneCrossing', "relatedInferences: ['c8f074e8575d4266a6010d5ed0ea6daf']", 'zoneCount: 1']
[AIXC] [2021-05-12 18:47:50,711] [MainThread  ] [INFO]: EVENT - Zone3: ['inferenceId: e3f983a0c2fd45b9b0bba9a4d8939d71', 'subtype: zoneCrossing', "relatedInferences: ['34cd8129edc34bfe8c96c49600a251df', 'a1e278d7b68d4eefbfbff35e80086a94', '697329a697694649aff3f25703bf9b16', '8e9323d8ed264b648887ede89767b830', '40f8d54d302b4438845046b991de48ee', 'fd2c302794184209b58c6b922ae1ae8c', 'e3e9f520defd4642a09f2bf702ec23f4']", 'zoneCount: 7']
```

#### VA Serving Rendered Pipeline

Adding a configuration parameter to specify the frame-destination enables a secondary workflow, with VA Serving rendering visualization of regions and entity detections/events (shown below).

By setting `enable_watermark` and `frame-destination` parameter for RTSP re streaming, the caller may visualize the output. This added to the `zones-spatial-analytics-rendered.json` extension configuration. So following the same instructions above but swapping the extension configuration used will dynamically produce the scene using rudimentary markers/dots showing the boundary of the defined polygon regions. This allows the DL Streamer `gvawatermark` element (used in the frame-destination) to handle rendering.

> gvawatermark does not draw the polygon lines, so the view must currently "connect the dots" themself.

  We add a label when a detection entity intersects or is within a defined region.

1. Run server:

   ```
   $ ENABLE_RTSP=true ./samples/lva_ai_extension/docker/run_server.sh
   ```

2. Run client with example extension configuration, with rendering support:

   ```
   $ ./samples/lva_ai_extension/docker/run_client.sh \
     --extension-config /home/video-analytics-serving/samples/lva_ai_extension/client/extension-config/zones-vaserving-rendered.json \
     --sample-file-path https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
   ```
3. Connect and visualize: Re-stream pipeline using VLC network stream with url `rtsp://localhost:8554/zone-events`.