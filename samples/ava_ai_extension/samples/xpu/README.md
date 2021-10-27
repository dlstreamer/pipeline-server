# XPU Operation with DL Streamer AI Extension

This sample concurrently runs three pipelines on three inference accelerator devices.

## Option 1
Operations file [operations-DetectionCPU-ClassificationVPU-TrackingiGPU--Option1.json](operations-DetectionCPU-ClassificationVPU-TrackingiGPU--Option1.json)

|Pipeline Name    |Pipeline Version             |Device|Media|
|-----------------|-----------------------------|------|-----|
|object_detection |object_zone_count_vehicle    |CPU   |[Parking Lot 2](https://lvamedia.blob.core.windows.net/public/lots_015.mkv)|
|object_classification |vehicle_attributes_recognition|NCS2  |[Parking Lot 2](https://lvamedia.blob.core.windows.net/public/lots_015.mkv)|
|object_tracking |person_vehicle_bike_tracking|GPU  |[People in waiting room 2](https://lvamedia.blob.core.windows.net/public/2018-03-05.10-05-01.10-10-01.bus.G331.mkv)|


## Option 2
Operations file [operations-DetectionCPU-DetectioniGPU-TrackingVPU--Option2.json](operations-DetectionCPU-DetectioniGPU-TrackingVPU--Option2.json)

|Pipeline Name    |Pipeline Version             |Device|Media|
|-----------------|-----------------------------|------|-----|
|object_detection |object_zone_count_vehicle    |CPU   |[Parking Lot 2](https://lvamedia.blob.core.windows.net/public/lots_015.mkv)|
|object_detection |person_vehicle_bike_detection|GPU   |[Home 1](https://lvamedia.blob.core.windows.net/public/homes_00425.mkv)|
|object_tracking |person_vehicle_bike_tracking  |NCS2  |[People in waiting room 2](https://lvamedia.blob.core.windows.net/public/2018-03-05.10-05-01.10-10-01.bus.G331.mkv)|


## Notes
> GPU driver will self-configure on the first run causing a 30s delay, so use single frame or short video to warm the pipeline.
