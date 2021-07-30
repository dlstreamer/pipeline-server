
# Creating Extensions
| [Events](#events) | [ Extensions ](#extensions) | [Adding Extensions to Pipelines](#adding-extensions-to-pipelines) | [References](#references) |

Extensions are a simple way to add functionality to a DL Streamer
pipeline using it's [python
bindings](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/Python)
and [GVAPython
element](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvapython). By
extending pipelines using `gvapython` a developer can access and alter
frames as they pass through a pipeline, add or change metadata such as
detected objects or JSON messages. The DL Streamer [gvapython
samples](https://github.com/openvinotoolkit/dlstreamer_gst/blob/master/samples/gst_launch/gvapython/face_detection_and_classification/README.md)
provide more examples of the full breadth of capabilities.
  
# Creating an Object Count Exceeded Extension

The following sections demonstrate how to create an extension that
detects when the number of objects in a frame exceeds a specific
threshold and how to publish that event using the
[`gva_event_meta`](/extensions/gva_event_meta/gva_event_meta.py) module along with
[`gva_event_convert`](/extensions/gva_event_meta/gva_event_convert.py),  [`gvametaconvert`](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvametaconvert)
and [`gvametapublish`](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvametapublish).

## Events

Events are a new type of metadata that can be added and read from a
frame using methods from the
[`gva_event_meta`](/extensions/gva_event_meta/gva_event_meta.py)
module. As they are in preview, their schema may change but they
illustrate how to add and publish additional information using the
underlying DL Streamer python bindings. 

Events are also used to publish results of the new set of Video
Analytics Serving spatial analytics extensions: [object_line_crossing](/extensions/spatial_analytics/object_line_crossing.md)
and [object_zone_count](/extensions/spatial_analytics/object_zone_count.md).

## Event Schema

Events are added to a frame and stored as a JSON message containing a
list of event objects. The only required key is `event-type` which is
the type of event. It is defined by the extension. An optional field
is `related-objects` which is an array of indices to the list of
detected objects. This allows a many-to-many relationship between
events and the objects that create them (e.g. a social distancing
algorithm would have one violate event and a number of objects that
were too close to each other).

```json
{
 "$schema": "https://json-schema.org/draft/2019-09/schema",
  "type": "array",
  "items" : {
    "properties": {
      "event-type": {
        "description": "Event type, known by caller",
        "type": "string"
      },
      "related-objects": {
        "description": "Array of related detections, each entry refers to index of associated detected object",
        "type" : "array",
        "items" : {
          "type" : "integer"
        }
      },
    },
    "required": [
      "event-type"
    ],
    "additionalProperties": true
  }
}
```

Here is an example of how events are added to existing metadata showing an event type `object-count-exceeded` with two related objects.

```json

"objects": [
	{"detection":{"bounding_box":{"x_max":0.4753129482269287,"x_min":0.306820273399353,"y_max":0.9987226724624634,"y_min":0.5475195646286011},"confidence":0.8045234084129333,"label":"person","label_id":1},"h":195,"roi_type":"person","w":129,"x":236,"y":237},
	{"detection":{"bounding_box":{"x_max":0.4753129482269287,"x_min":0.306820273399353,"y_max":0.9987226724624634,"y_min":0.5475195646286011},"confidence":0.8045234084129333,"label":"person","label_id":1},"h":195,"roi_type":"person","w":129,"x":200,"y":237}
],

"events": [
      {
          "event-type": "object-count-exceeded",
          "related-objects": [
              0,
              1
          ]
      }
]
```

## Extensions
An extension is a GVA Python script that is called during pipeline
execution. The script is given a frame and any VA Serving parameters
defined by the pipeline request. The following example generates an
event type `object-count-exceeded` if more than a pre-defined number
of objects are detected in a frame.

A couple of things to note:

* The `threshold` pipeline parameter is picked up in the
  constructor. Other parameters can be accessed in the same way.
* Use of the [`gva_event_meta`](/extensions/gva_event_meta/gva_event_meta.py) module's function `add_event()` to populate an event object.

```python
import gva_event_meta

class ObjectCounter:
    def __init__(self, threshold):
        self._threshold = threshold

    def process_frame(self, frame):
        num_objects = len(list(frame.regions()))
        if num_objects > self._threshold:
            gva_event_meta.add_event(frame,
                                      event_type="object_count_exceeded")
```

## Adding Extensions to Pipelines

The extension must be added after the last element that generates data
it requires. As events are not part of the DL Streamer message schema
we also add an extension called [`gva_event_convert`](/extensions/gva_event_meta/gva_event_convert.py)
after [`gvametaconvert`](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvametaconvert)
and before [`gvametapublish`](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/gvametapublish). This
reusable extension adds an event list to the published result.

A pipeline using a sample object counting extension would look like this:

![diagram](images/object_counter_pipeline.png)

and the template would look like this:
```
"template": ["uridecodebin name=source",
  "! gvadetect model={models[object_detection][person_vehicle_bike][network]} name=detection",
  " ! gvapython class=ObjectCounter module=/home/video-analytics-serving/extensions/object_counter.py name=object-counter",
  " ! gvametaconvert name=metaconvert",
  " ! gvapython module=/home/video-analytics-serving/extensions/gva_event_meta/gva_event_convert.py",
  " ! gvametapublish name=destination",
  " ! appsink name=appsink"],
```

## References

For details on more advanced extensions, see the [line crossing](/extensions/spatial_analytics/object_line_crossing.py) and [zone counting](/extensions/spatial_analytics/object_zone_count.py). These include more
complex parameters, guidance on how to break down algorithmic
implementation to simplify event generation and how to use
watermarking for visualizing output.

Note also how the pipeline definition is used to validate parameter schemas. 

See [object_line_crossing.md](/extensions/spatial_analytics/object_line_crossing.md)
and [object_zone_count.md](/extensions/spatial_analytics/object_zone_count.md) for
more information and a format for extension documentation.
