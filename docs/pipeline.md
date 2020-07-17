# Customizing Pipelines
VA Serving pipelines are a sequence of processing elements used to implement a video analytics solution. 
This document explains how pipelines are described and how they refer to models.
This document is broken into a number of sections:
* [Model Discovery](#model-discovery): How VA Serving finds models and how pipelines refer to them.
* [GStreamer](#gstreamer): A quick backgrounder on the GStreamer media framework.
* [Pipeline Description Files](#pipeline-description-files): Syntax of pipeline definition files.

## Model Discovery
VA Serving discovers models using the directory structure below:
* Root folder name is `models`. This can be specified at build or run time.
* Model name is `emotion_recognition`
* Model version is `1`
* Model proc file `emotions-recognition-retail-0003.json` is in root folder as it is used by all model precisions.
* Bin and network files are in directories named after precision (e.g. INT8, INT16 etc.)
```
models/
├── emotion_recognition                                           // name
│   └── 1                                                         // version
│       ├── emotions-recognition-retail-0003.json                 // proc file
│       ├── FP16                                                  // precision
│       │   ├── emotions-recognition-retail-0003-fp16.bin         // bin file
│       │   └── emotions-recognition-retail-0003-fp16.xml         // network file
│       ├── FP32
│       │   ├── emotions-recognition-retail-0003.bin
│       │   └── emotions-recognition-retail-0003.xml
│       └── INT8
│           ├── emotions-recognition-retail-0003-int8.bin
│           └── emotions-recognition-retail-0003-int8.xml
```
Pipeline definitions refer to model files using a multi-dimensional array in the format `[name][version][precision][file-type]` 
or if default precision is used `[name][version][file-type]`. For CPU default precision is FP32 and for other accelerators it is FP16.
* `name` is name of model (emotion_recognition in above example)
* `version` is version number (1 in above example)
* `file-type` is one of `network`, `bin` or `proc`

Some examples:
* [emotion_recognition][1][proc] expands to emotions-recognition-retail-0003.json
* If running on CPU [emotion_recognition][1][network] expands to emotions-recognition-retail-0003.xml
* Running on GPU [emotion_recognition][1][network] expands to emotions-recognition-retail-0003-fp16.xml
* [emotion_recognition][1][INT8][network] expands to emotions-recognition-retail-0003-int8.xml


## GStreamer 
### Background
[GStreamer](https://gstreamer.freedesktop.org/) is a flexible, fast and multi-platform open-source multimedia framework. 
It has an easy to use command line tool for running pipelines, as well as an API with bindings in C, Python, 
Javascript and [more](https://gstreamer.freedesktop.org/bindings/).

Pipelines use the syntax of the GStreamer command line tool gst-launch-1.0.  The list of elements, their configuration properties, and their connections are all specified as a list of strings separated by exclamation marks (!).  Internally the GStreamer library constructs a pipeline object that contains the individual elements and handles common operations such as clocking, messaging, and state changes.

**Example:** ```gst-launch-1.0 videotestsrc ! ximagesink```

For more information and examples please refer to the [gst-launch-1.0](https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html?gi-language=c) online documentation.

### Elements
An [element](https://gstreamer.freedesktop.org/documentation/application-development/basics/elements.html?gi-language=c) is the fundamental building block of a pipeline. Elements performs specific operations on incoming frames and then push the resulting frames 
downstream for further processing. Elements are linked together textually by exclamation marks (`!`) with the full chain of elements 
representing the entire pipeline. Each element will take data from its upstream element, process it and then output the data for further processing by the next element.

Elements designated as **source** elements provide input into the pipeline from external sources. In this tutorial we use the [filesrc](https://gstreamer.freedesktop.org/documentation/coreelements/filesrc.html?gi-language=c#filesrc) element that reads input from a local file.

Elements designated as **sink** elements represent the final stage of a pipeline. As an example a sink element could write transcoded 
frames to a file on the local disk or open a window to render the video content to the screen or even re-stream the content via rtsp. 
In this tutorial our primary focus is to compare the performance of media analytics pipelines on different types of hardware and we will 
use the standard [fakesink](https://gstreamer.freedesktop.org/documentation/coreelements/fakesink.html?gi-language=c#fakesink) element to end the pipeline immediately after the analytics is complete without further processing.

Object detection pipelines typically use the [decodebin](https://gstreamer.freedesktop.org/documentation/playback/decodebin.html#decodebin) utility element 
to construct a set of decode operations based on the given input format, decoder and demuxer elements available in the system. 
The next step in the pipeline is often color space conversion which is handled by the 
[videoconvert](https://gstreamer.freedesktop.org/documentation/videoconvert/index.html?gi-language=c#videoconvert) element. 

### Properties
Elements are configured using key-value pairs called properties. As an example the `filesrc` element has a property named `location` which specifies the file path for input.

**Example**:
 ```filesrc location=cars_1900.mp4```

A list of properties supported by each element can be viewed using the command line tool `gst-inspect-1.0`. The tool also provides a property description and the valid range of values that can be set.

## Pipeline Description Files

Pipelines are defined using JSON and comprise four top level attributes:

|Attribute|Notes|
|---------|-----|
|type|Framework type. Can be either `GStreamer` or `FFmpeg`|
|description|Brief description of pipeline|
|template|Pipeline template (i.e. pipeline without source or sink)|
|parameters|Optional attribute than sets element properties|

The type and description attributes are self explanatory, however `template` and `parameters` are more complex and will be described below.

### Template
The template attribute describes the pipeline and is specific to the underlying framework. 
The `source` and `sink` elements in a pipeline template intentionally avoid assigning explicit media source and destination. This enables the properties to be dynamically defined by the calling application. 
This will be covered in the API section. Templates use the gst-launch format to concatenate elements to form a pipeline. The VA Serving `pipeline manager` component parses the template, configures the source and sink elements and then constructs pipeline. 

Here is the template for the `object_detection` sample pipeline.
We'll focus on some of the elements to help explain how a template is parsed and
constructed. 
```
"template" : "urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert ! gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination file-format='json-lines' ! appsink name=appsink"
```
The `name` property is used by the `parameters` attribute to determine which element a property should be applied to. More details in the [Parameters](#parameters) section. 

The element property `name` has special value `source` which is replaced by the video source URI provided by the calling application. You can see it being used by the `urisourcebin` element.

Now look at the `gvadetect` element an example for an example of how properties are used.
```
gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection 
```
The `model` property needs path to a model file and uses the array syntax explained in the [Model Discovery](#model-discovery) section. It is enclosed with curly brackets to indicate the value is a variable rather than a path.

#### Improving Template Readability
If there are a large number of elements in a template it can become hard to read. A way to improve readability is to use `array format` 
where each GStreamer element becomes an array element. The above `object_detection` sample pipeline would now look like this:

```
"template" : [ "urisourcebin name=source",
  "! concat name=c",
  "! decodebin",
  "! video/x-raw",
  "! videoconvert name=videoconvert",
  "! gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection",
  "! gvametaconvert name=metaconvert",
  "! queue",
  "! gvametapublish name=destination file-format='json-lines'",
  "! appsink name=appsink"
]
```

### Parameters
This is an optional attribute named `parameters` that is used by the template to set property values for pipeline elements. 
The attribute is in JSON schema format which enables its validation. The attribute is used in two ways:
1. To validate property values passed in via API.
2. To define default property values that are applied to element during pipeline construction.

The attribute contains two sub-attributes `type` and `properties`. 
`type` is always the string value `"object"` and `properties` is a list of element properties.

#### Properties
The `properties` attribute is a list of element properties. Each attribute in the list is an element property name whose value is an object.
The object must have the following attributes:
* `element` a string that must match the name of an element in the pipeline
* `type` property type, either `integer` or `boolean`
  * if type is `integer` 
    * attributes `minimum`, `maximum` must also be supplied in integer format
    * attribute `default` is optional. If supplied must match schema and if so is applied to element.
  * if type is boolean then a `default` attribute must be supplied in boolean format

This is a sample parameter from the `emotion_recognition` sample pipeline that contains a single property `inference-interval`
```json
"parameters": {
    "type": "object",
    "properties": {
        "inference-interval": {
            "element": "detection",
            "type": "integer",
            "minimum": 0,
            "maximum": 4294967295,
            "default": 1
        }
    }
}
```
This sets the property `inference-interval` in the element named `detection` to the default value of 1. 
It is a valid value as it is between 0 and 4294967295.

