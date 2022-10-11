#!/bin/bash

curl http://localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H "Content-Type: application/json" -d '{
   "source":{
      "uri":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type":"uri"
   },
   "parameters": {
      "detection-device": "CPU",
      "detection-model-instance-id": "detect_object_detection_person_vehicle_bike_CPU"
   }
}'
