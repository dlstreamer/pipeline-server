#!/bin/bash

curl http://localhost:8443/pipelines/object_detection/person_vehicle_bike -X POST -H "Content-Type: application/json" -d '{
   "source":{
      "uri":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type":"uri"
   },
   "destination":{
      "frame":{
         "type":"rtsp",
         "path":"view01"
      }
   },
   "parameters": {
      "detection-device": "CPU",
      "detection-model-instance-id": "detect_object_detection_person_vehicle_bike_GPU"
   }
}'
