## Script Arguments

The `./samples/edgex_bridge/edgex_bridge.py` script accepts the following command line parameters.

```code
usage: edgex_bridge.py [-h] [--source SOURCE] [--destination DESTINATION]
                       [--edgexdevice EDGEXDEVICE]
                       [--edgexcommand EDGEXCOMMAND]
                       [--edgexresource EDGEXRESOURCE] [--topic TOPIC]
                       [--generate]

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       URI describing the source media to use as input.
                        (default: https://github.com/intel/dlstreamer-pipeline-server/raw/master/samples/bottle_detection.mp4)
  --destination DESTINATION
                        address of MQTT broker listening for edgex inference
                        results. (default: localhost:1883)
  --edgexdevice EDGEXDEVICE
                        Device name registered with edgex-device-mqtt.
                        (default: videoAnalytics-mqtt)
  --edgexcommand EDGEXCOMMAND
                        EdgeX command declared in the device profile.
                        (default: videoAnalyticsData)
  --edgexresource EDGEXRESOURCE
                        EdgeX device resource declared in the device profile.
                        (default: videoAnalyticsData)
  --topic TOPIC         destination topic associated with EdgeX Core Data
                        (default: objects_detected)
  --generate            Generate EdgeX device profile for device-mqtt. Also populates docker.compose.override.yml
  --rtsp-path           Instructs VA Serving to render frames to RTSP at the supplied URI path segment (e.g., edgex_event_emitter).
                        (default: None)
  --analytics-image     Analytics image name to use for uService deployment to Docker compose.
                        (default: dlstreamer-pipeline-server-edgex:latest)
  --analytics-container Analytics container name to use for uService deployment to Docker compose.
                        (default: edgex-dlstreamer-pipeline-server)
```
