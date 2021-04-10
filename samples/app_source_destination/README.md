# App Source and Destination Sample

VA Serving source and destination definitions support a type `application` which allows programmatic interaction with the vaserving library.

## Source
The source will be given access to a queue instantiated by the application. The source must be aware of the frame type so it can be converted to a GStreamer object
if necessary. The extension class and queue object (`src_queue` in snippet below) are specified as part of the source field in the request made by the caller when starting the pipeline. The source expects a queue of Gstreamer objects that must contain one of the following types:
* GvaFrameData
* GvaSample
* Gst.Sample
* Gst.Buffer

Assuming source queue object is `src_queue` the source request object would look like this
```
source = {
    "type": "application",
    "class": "GStreamerAppSource",
    "input": src_queue
}
```

## Destination
Similar to the source, the app destination takes a queue defined by the application. Destination properties are defined as follows:
* **type**: always "application"
* **class**: the class name of the extension (GStreamerAppDestination)
* **output**: the queue object that extension should place results in
* **mode**: the type of result, defined as follows
  * **frames**: a GVASample object (default)
  * **regions**: a list of inference regions
  * **tensors**: a list of inference tensors
  * **messages**: a list of inference messages

The destination queue will provide [GVA VideoFrames](https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/python/gstgva/video_frame.py).

The destination part of the request object would look like this:
```
destination = {
    "type": "application",
    "class": "GStreamerAppDestination",
    "output": dst_queue
    "mode": "frames"
}
```
The destination will signal and of stream (EOS) by sending a null result.


## Pipeline
Here is a sample pipeline. To be ready for for `application` source and destination the template must define source to be `appsrc` and sink to be `appsink`.
```json
{
    "type": "GStreamer",
    "template": ["appsrc name=source",
		 " ! gvadetect model={models[object_detection][person_vehicle_bike][network]} name=detection",
		 " ! appsink name=destination"],
    "description": "Person Vehicle Bike Detection"
}
```

## Sample Code
The sample shows how to programmatically supply frames to VA Serving GStreamer pipelines and receive resulting frames and meta-data.
It uses a neat trick of using one pipeline (`video_decode/app_dst`) to decode the source media
and another (`object_detection/app_src_dst`) to receive the resulting frames and produce inference meta-data.
The destination queue from `video_decode/app_dst` feeds into source queue for `object_detection/app_src_dst` which outputs into a result queue
whose contents are displayed.

To run, do the following:
```
$ docker/build.sh
<snip>
$ docker/run.sh --dev
<snip>
openvino@host:~$ python3 samples/app_source_destination/app_source_destination.py
{"levelname": "INFO", "asctime": "2021-04-09 05:24:43,626", "message": "Creating Instance of Pipeline object_detection/app_src_dst", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-09 05:24:43,628", "message": "Creating Instance of Pipeline video_decode/app_dst", "module": "pipeline_manager"}
{"levelname": "INFO", "asctime": "2021-04-09 05:24:43,908", "message": "Setting Pipeline 2 State to RUNNING", "module": "gstreamer_pipeline"}
{"levelname": "INFO", "asctime": "2021-04-09 05:24:44,495", "message": "Setting Pipeline 1 State to RUNNING", "module": "gstreamer_pipeline"}
Frame: sequence_number:0 timestamp:1617945883.7153962
        Detection: Region = Rect(x=187, y=555, w=253, h=345), Label = person
        Detection: Region = Rect(x=1149, y=571, w=244, h=365), Label = person
        Detection: Region = Rect(x=447, y=495, w=177, h=208), Label = person

Frame: sequence_number:1 timestamp:1617945883.7554579
        Detection: Region = Rect(x=185, y=554, w=255, h=344), Label = person
        Detection: Region = Rect(x=1150, y=570, w=243, h=365), Label = person
        Detection: Region = Rect(x=447, y=495, w=177, h=207), Label = person

Frame: sequence_number:2 timestamp:1617945883.7937195
        Detection: Region = Rect(x=185, y=553, w=255, h=345), Label = person
        Detection: Region = Rect(x=1150, y=570, w=243, h=364), Label = person
        Detection: Region = Rect(x=448, y=495, w=176, h=206), Label = person
<snip>
```
