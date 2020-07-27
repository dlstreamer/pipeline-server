# Pipeline Definition
VA Serving pipelines are a sequence of processing elements used to implement a video analytics solution. 
This document explains how pipelines are described and how they refer to models.
This document is broken into a number of sections:
* [Model Discovery](#model-discovery): How VA Serving finds models and how pipelines refer to them.
* [GStreamer](#gstreamer): A quick backgrounder on the GStreamer media framework.
* [Pipeline Description Files](#pipeline-description-files): Syntax of pipeline definition files.

## Model Discovery
Deep learning models can be stored in a number of formats, usually defined by the inference framework that uses them.
[ONNX*](https://onnx.ai/), [PyTorch*](https://pytorch.org/) and [TensorFlow*](https://www.tensorflow.org/) are some examples. 
The OpenVINO* inference engine used by VA Serving uses a format called [Intermediate Representation](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_IR_and_opsets.html) (IR) that comprises a `bin` file for the model and metadata in XML format termed a `network file`. Models are encoded with a `precision` which can be floating point or integer and have a range of bit widths. Finally models have an optional `model-proc` file which defines supported input formats and describes the output thus ensuring they are 
compatible with upstream and downstream elements.  

VA Serving discovers models using the directory structure below for a sample model.
* Root folder name is `models`. This can be specified at build or run time.
* Model name is `emotion_recognition`
* Model version is `1`
* Model proc file `emotions-recognition-retail-0003.json` is in root folder as it is used by all model precisions.
* IR bin and network files are in directories named after precision (e.g. INT8, INT16 etc.)
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

## Pipeline Description Files
Pipelines are defined using JSON and comprise four top level attributes:

|Attribute|Notes|
|---------|-----|
|type|Framework type. Can be either [GStreamer](./gstreamer.md) or [FFmpeg](https://ffmpeg.org/ffmpeg.html)|
|description|Brief description of pipeline|
|template|Pipeline template (i.e. pipeline without source or sink)|
|parameters|Optional attribute than sets element properties|

The type and description attributes are self explanatory, however `template` and `parameters` are more complex and will be described below.

Description files are always named `pipeline.json` and laid out in the following directory structure: `framework/name/version/pipeline.json`. 
Here is a sample directory listing:
```
pipelines/
├── ffmpeg
│   ├── emotion_recognition
│   │   └── 1
│   │       └── pipeline.json
│   └── object_detection
│       └── 1
│           └── pipeline.json
└── gstreamer
    ├── audio_detection
    │   └── 1
    │       └── pipeline.json
    ├── emotion_recognition
    │   └── 1
    │       └── pipeline.json
    └── object_detection
        └── 1
            └── pipeline.json
```
### Template
The template attribute describes the pipeline and is specific to the underlying framework. Templates use the concept of a media framework `source` and `sink`. A source provides media input into the pipeline and a sink represents the final stage of a pipeline. VA Serving configures the source component to select the media and the sink component to set the pipeline's output destination. GStreamer and FFMpeg templates will be documented in the following sections.

#### GStreamer Template
This section assumes an understanding of the GStreamer framework. If you are new to GStreamer you can get some background by reading [this overview](./gstreamer.md).

Templates use the [GStreamer pipeline description](https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html?gi-language=c#pipeline-description) syntax to concatenate elements to form a pipeline. The VA Serving `pipeline manager` component parses the template, configures the source and sink elements and then constructs pipeline. 

The `source` and `sink` elements in a pipeline template intentionally avoid assigning explicit media source and destination. This enables the properties to be dynamically defined by the calling application. 

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

#### FFmpeg Template
A full description of FFmpeg pipeline templates will be provided in a later release. 
Conceptually templates are similar to GStreamer but the gst-launch string is replaced by an [FFmpeg command line](https://ffmpeg.org/ffmpeg.html).

#### Improving Template Readability
If there are a large number of elements in a template it can become hard to read. A way to improve readability is to use `array format` 
where each GStreamer element becomes an array element. The GStreamer `object_detection` sample pipeline would now look like this:

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
Each attribute in the list is an element property name whose value is an object.
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
This sets the property `inference-interval` in the element named `detection` to a value of 1. 
It is a valid value as it is between 0 and 4294967295.

### Reserved Parameter Properties
#### bus-messages
This is a boolean property specific to GStreamer pipelines. If set to true GStreamer element bus messages will be sent to stdout. 
This is useful for debugging pipelines that work with gst-launch but not in the VA Serving environment. If `default` key not set `bus-messages` defaults to `false`. 
```json
"parameters": {
	  "type": "object",
	  "properties": {
		  "bus-messages": {
			  "type": "boolean",
			  "default": true
      }
    }
}
```
You must add the `bus-messages` property to the pipeline description file's `parameters attribute` and set it to `true` for message logging to work.
Currently only the `audio_detection` pipeline includes the bus-messages property.

This example shows how to use `bus-messages` property to disable message logging in the audio pipeline with curl request. 
```bash
curl localhost:8080/pipelines/audio_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "parameters":{"bus-messages":false}}'
```

## Legal Information
[*] Other names and brands may be claimed as the property of others.
