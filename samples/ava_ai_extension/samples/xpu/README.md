# XPU Operation with DL Streamer AI Extension

This sample concurrently runs three pipelines on three inference accelerator devices.

|Pipeline Name    |Pipeline Version             |Device|Media|
|-----------------|-----------------------------|------|-----|
|object_detection |object_zone_count_person     |CPU   |[People in waiting room 2](https://lvamedia.blob.core.windows.net/public/2018-03-05.10-05-01.10-10-01.bus.G331.mkv)|
|object_detection |object_zone_count_vehicle    |GPU   |[Parking Lot 2](https://lvamedia.blob.core.windows.net/public/lots_015.mkv)|
|object_detection |person_vehicle_bike_detection|NCS2  |[Home 1](https://lvamedia.blob.core.windows.net/public/homes_00425.mkv)

## Notes
> GPU driver will self-configure on the first run causing a 30s delay, so use single frame or short video to warm the pipeline.
