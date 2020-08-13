# Defining Media Analytics Pipelines
| [Pipeline Definition Files](#pipeline-definition-files) | [Pipeline Discovery](#how-pipeline-definition-files-are-discovered-and-loaded) | [Pipeline Templates](#pipeline-templates) | [Pipeline Parameters](#pipeline-parameters) | [Deep Learning Models](#deep-learning-models) | 

Media analytics pipelines are directed graphs of audio/video
processing, computer vision, and deep learning inference
operations. The following sections explain how media analytics
pipelines are defined and loaded by Video Analytics Serving.

# Pipeline Definition Files
Pipeline definition files are JSON documents containing a single
top-level object with four sections.

|Section | Value |
|---------|-----|
|type|Framework type. <br/> <br/> Can be either [GStreamer](https://gstreamer.freedesktop.org/documentation/?gi-language=c)* or [FFmpeg](https://ffmpeg.org/)* |
|description|Brief description of pipeline.|
|template|Pipeline graphs and operations as described in the syntax of the media analytics framework. <br/> <br/> For `GStreamer` this is the `PIPELINE-DESCRIPTION` syntax supported by  [`gst-launch-1.0`](https://gstreamer.freedesktop.org/documentation/tutorials/basic/gstreamer-tools.html#gstlaunch10). For a brief `GStreamer` introduction please see the following [overview](gstreamer_overview.md). <br/> <br/> For `FFmpeg` this is the syntax of the [`ffmpeg`](https://ffmpeg.org/ffmpeg.html#toc-Synopsis) command-line tool. 
|parameters|Optional JSON object specifying pipeline parameters that can be customized when the pipeline is launched.|

## How Pipeline Definition Files are Discovered and Loaded

Pipeline definition files are stored in a hierarchical directory
structure that determines their name and version. On startup, the
Video Analytics Serving `pipeline_manager` searches the configured
pipeline directory and loads all pipeline definitions that are found.

The hierarchical directory structure is made up of three levels:

`<pipeline-root-directory>/<pipeline-name>/<version>/<pipeline>.json`. 

Here is a sample directory listing:
```
pipelines/gstreamer
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

> **Note:** When a Video Analytics Serving application needs to support
> multiple frameworks their pipelines are typically stored in separate
> top-level directories and built into separate docker images.

> **Note:** While not required, pipeline definition files are named
> `pipeline.json` by convention.


## Pipeline Templates
The template property within a pipeline definition describes the order
and type of operations in the media analytics pipeline. The syntax of
the template property is specific to the underlying framework
(`GStreamer` or `FFmpeg`). Templates use the `source`,
`destination` and `parameters` sections of an incoming pipeline
`request` to customize the source, destination and behavior of a
pipeline implemented in an underlying framework. The Video Analytics
Serving `pipeline_manager` and framework specific modules
`gstreamer_pipeline` and `ffmpeg_pipeline` provide default handling
for typical `source` and `destination` options.

### GStreamer Templates

> **Note:** This section assumes an understanding of the GStreamer
> framework.  Developers new to GStreamer can start with a brief 
> [GStreamer overview](./gstreamer_overview.md).


GStreamer templates use the [GStreamer Pipeline
Description](https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html?gi-language=c#pipeline-description)
syntax to concatenate elements into a pipeline. The Video Analytics
Serving `pipeline_manager` and `gstreamer_pipeline` modules
parse the template, configure the `source`, `destination`, and
`appsink` elements and then construct the pipeline based on incoming
requests.

The `source`, `destination` and `appsink` elements in a pipeline template
intentionally avoid assigning explicit media source and destination
properties. This enables the properties to be dynamically defined by
the calling application.

#### Object Detection
**Example:**
```
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert",
				" ! gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection",
				" ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination",
				" ! appsink name=appsink"
				]
```

#### Element Names

Each element in a GStreamer pipeline has a name that is either
generated automatically or set by using the standard element property:
`name`. Using the `name` property in a template creates an explicit
alias for the element that can then be used in the `parameters`
section of a pipeline definition. More details on parameters can be
found in the [Parameters](#parameters) section.

Certain element names also trigger special default handling by the
Video Analytics Serving modules. For example in the `object_detection`
sample template the special element name `source` results in the
`urisourcebin`'s `uri` property getting automatically set to the
source uri of an incoming request.

#### Element Properties

Each element in a GStreamer pipeline can be configured through it's
set of properties.

The `object_detection` template demonstrates how to set the
`gvadetect` element's properties to select the deep learning model
used to detect objects in a video frame.

```
gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection 
```

The `model` and `model-proc` properties reference file paths to the
deep learning model as discovered and populated by the Video Analytics
Serving `model_manager` module. The `model_manager` module provides a
python dictionary associating model names and versions to their
absolute paths enabling pipeline templates to reference them by
name. More details are provided in the [Deep Learning Models](#deep-learning-models) section.

#### More Information

For more information and examples of media analytics pipelines created
with DL Streamer please see the DL Streamer [tutorial](https://github.com/opencv/gst-video-analytics/wiki/GStreamer%20Video%20Analytics%20Tutorial).

### FFmpeg Templates

> **Note:** A more full description of FFmpeg pipeline templates will
> be provided in a later release.

 Conceptually FFmpeg templates are similar to GStreamer templates but
 the gst-launch string syntax is replaced by the [FFmpeg
 Command-Line](https://ffmpeg.org/ffmpeg.html) syntax.
 
#### Object Detection
**Example:**

```
"template": [
	"-i \"{source[uri]}\" ",
	"-vf \"detect=model={models[object_detection][1][network]}",
	":model_proc=\"{models[object_detection][1][proc]}\":interval={parameters[inference-interval]}\",",
	"metaconvert",
	" -an -y -f metapublish"
    ]
```

#### More Information

For more information and examples of media analytics pipelines created
with FFmpeg Video Analytics please see the FFmpeg Video Analytics
[getting started
guide](https://github.com/VCDP/FFmpeg-patch/wiki/Getting-Started-Guide-%5Bv0.5-2020%5D).
 
 

## Pipeline Parameters

Pipeline parameters enable developers to customize pipelines based on
incoming requests. Parameters are an optional section within a
pipeline definition and are used to specify which pipeline properties
are configurable and what values are valid. Developers can also
specify default values for each parameter.

### Defining Parameters as JSON Schema

The `parameters` section in a pipeline definition provides the JSON
schema used to validate the `parameters` in a request. It can also
provide details on how those parameters are interpreted by the
`gstreamer_pipeline` or `ffmpeg_pipeline` modules.

The `parameters` section of a pipeline request is a JSON object. The
`parameters` section of a pipeline definition is the JSON schema for
that JSON object. For more details on JSON schemas please refer to JSON schema
[documentation](https://json-schema.org/understanding-json-schema/reference/object.html).


**Example:** 

The following `parameters` section contains two parameters: `height`
and `width`:

```json
"parameters": {
    "type": "object",
    "properties": {
        "height": {
            "type": "integer",
            "minimum": 200,
            "maximum": 400,
            "default": 200
        },
        "width": {
            "type": "integer",
            "minimum": 400,
            "maximum": 600,
            "default": 400
        }
    }
}
```

Once defined these parameters can be used in a pipeline template by
direct substitution.

```json
"template": [   " urisourcebin name=source ! concat name=c ! decodebin ! videoscale",
                " ! video/x-raw,height={parameters[height]},width={parameters[width]}",
                " ! appsink name=appsink"
            ]	
```


### Special Handling for Media Frameworks

In addition to specifying the `type`, `default` and `allowed values`
in JSON schema notation, pipeline parameters can also include
properties that determine how they are interpreted by media analytics
frameworks.

#### Parameters and GStreamer Elements

Parameters in GStreamer pipeline definitions can include information
on how to associate a parameter with one or more GStreamer element
properties.

The JSON schema for a GStreamer pipeline parameter can include an
`element` section in one of three forms.

1. **Simple String**. <br/> <br/>
   The string indicates the `name` of an element in
   the GStreamer pipeline. The property to be set is taken from the
   parameter name.
   
   **Example:**
   
   The following snippet defines the parameter `inference-interval`
   which sets the `inference-interval` property of the `detection`
   element.
   
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
   
1. **Object**. <br/> <br/> The object indicates the element `name`,
   `property` and `format` for the parameter. The `format` is only
   required in special cases where the property value has to be
   formatted as a valid JSON document.
   
   **Example:**
   
   The following snippet defines the parameter `interval`
   which sets the `inference-interval` property of the `detection`
   element.
   
   ```json
   "parameters": {
   "type": "object",
   "properties": {
        "interval": {
            "element": {
                "name":"detection",
                "property":"inference-interval"
            },
            "type": "integer",
            "minimum": 0,
            "maximum": 4294967295,
            "default": 1
            }
        }
    }
	```
   
1. **Array** of Objects or Strings. <br/> <br/> An array specifying
   multiple element properties to be set by the same pipeline
   parameter.

   **Example:**
   
   The following snippet defines the parameter `interval` which sets
   the `inference-interval` property of the `detection` element and
   the `inference-interval` property of the `classification` element.
   
   ```json
   "parameters": {
   "type": "object",
   "properties": {
        "interval": {
            "element": 
                [ {"name":"detection",
                    "property":"inference-interval"},
                  {"name":"classification",
                   "property":"inference-interval"}
                ],
            "type": "integer",
            "minimum": 0,
            "maximum": 4294967295,
            "default": 1
            }
        }
    }
	```
#### Parameters and FFmpeg Filters

Parameters in FFmpeg pipeline definitions can include information on
how to associate a parameter with one or more FFmpeg filters.

The JSON schema for a FFmpeg pipeline parameter can include a
`filter` section in one of two forms.

1. **Object**. <br/> <br/> The object indicates the filter `name`,
   `type`, `property`, `index` and `format` for the parameter. The
   `format` is only required in special cases where the property value
   has to be formatted as a valid JSON document.
   
   **Example:**
   
   The following snippet defines the parameter `inference-interval` which sets
   the `interval` property of the first `detect` filter.
   
   ```json
   "parameters": {
   "type": "object",
   "properties": {
        "inference-interval": {
            "filter": {"name":"detect",
                       "type":"video",
                       "index":0,
                       "property":"interval"},
            "type": "integer",
            "minimum": 0,
            "maximum": 4294967295,
            "default": 1
            }
        }
    }
	```
   
1. **Array** of Objects. <br/> <br/> An array specifying
   multiple filter properties to be set by the same pipeline
   parameter.

   **Example:**
   
   The following snippet defines the parameter `interval` which sets
   the `interval` property of the `detect` filter and
   the `interval` property of the `classify` filter.
   
   ```json
   "parameters": {
   "type": "object",
   "properties": {
        "inference-interval": {
            "filter":[ {"name":"detect",
                        "type":"video",
                        "index":0,
                        "property":"interval"},
                       {"name":"classify",
                        "type":"video",
                        "index":0,
                        "property":"interval"}
                     ],
            "type": "integer",
            "minimum": 0,
            "maximum": 4294967295,
            "default": 1
            }
        }
    }
	```




### Parameter Resolution in Pipeline Templates

Parameters passed in through a request are resolved in a pipeline
template either through direct substitution or through special media
framework handling.

#### Direct Substitution

Wherever a value in a pipeline template is referenced through a key in
the parameters object it's value is taken from the incoming request or
is set to the specified default value.

**Example:**

Pipeline Template:

```json
"template": ["urisourcebin name=source uri={source[uri]} ! concat name=c ! decodebin ! videoscale"
             " ! video/x-raw,height={parameters[height]},width={parameters[width]}"
             " ! appsink name=appsink"
            ]	
```

Pipeline Parameters:
```json
"parameters": {
    "type": "object",
    "properties": {
        "height": {
            "type": "integer",
            "minimum": 200,
            "maximum": 400,
            "default": 200
        },
        "width": {
            "type": "integer",
            "minimum": 400,
            "maximum": 600,
            "default": 400
        }
     }
 }
```

Pipeline Request:
```json
{
  "source": {
   "type":"uri",
   "uri":"file:///temp.mp4"
  },
  "parameters": {
    "height":300,
    "width":300
  }
}
```

Parameter Resolution:

```
"urisourcebin name=source uri=file:///temp.mp4 ! concat name=c ! decodebin ! videoscale" \
" ! video/x-raw,height=300,width=300" \
" ! appsink name=appsink"
```


#### Media Framework Handling
When a parameter definition contains details on how to set GStreamer
`element` or FFmpeg `filter` properties, templates do not need to
explicitly reference the parameter.

**Example:**

Pipeline Template:

```json
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! videoscale"
             " ! video/x-raw,height=300,width=300"
             " ! appsink name=appsink"
            ]	
```

Pipeline Parameters:
```json
"parameters": {
    "type": "object",
    "properties": {
        "scale_method": {
            "type": "string",
            "element": { "name": "videoscale", "property": "method" },
            "enum": ["nearest-neighbour","bilinear"],
            "default": "bilinear"
        }
    }
}
```

Pipeline Request:
```json
{
 "source": {
  "type":"uri",
  "uri":"file:///temp.mp4"
 },
 "parameters": {
   "scale_method":"nearest-neighbour"
 }
}
```

Parameter Resolution:

> **Note:** Parameters defined this way are set via the GStreamer
> Python API. The following pipeline string is provided for
> illustrative purposes only.

```
"urisourcebin name=source uri=file:///temp.mp4 ! concat name=c ! decodebin ! videoscale method=nearest-neighbour" \
" ! video/x-raw,height=300,width=300" \
" ! appsink name=appsink"
```

### Reserved Parameters

The following parameters have built-in handling within the Video
Analytics Serving modules and should only be included in pipeline
definitions wishing to trigger that handling.

#### bus-messages

A boolean parameter that can be included in GStreamer pipeline
definitions to trigger additional logging for GStreamer bus messages.

If included and set to true, GStreamer bus messages will be logged
with log-level `info`. This is useful for elements which post messages
to the bus such as
[level](https://gstreamer.freedesktop.org/documentation/level/index.html?gi-language=c).

**Example:**

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


# Deep Learning Models

## OpenVINO<sup>&#8482;</sup> Toolkit's Intermediate Representation

Video Analytics Serving applications and pipelines use deep learning
models in the OpenVINO<sup>&#8482;</sup> Toolkit's [Intermediate
Representation](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_IR_and_opsets.html)
format (`IR`). A model in the `IR` format is represented by two files:

* `<model_name>.xml`. An XML file describing the model layers,
  precision and topology.
  
* `<model_name>.bin`. A binary file encoding a trained model's weights.

### Converting Models
For more information on converting models from popular frameworks into
`IR` format please see the OpenVINO<sup>&#8482;</sup> Toolkit
documentation for [model optimizer](https://docs.openvinotoolkit.org/latest/openvino_docs_MO_DG_Deep_Learning_Model_Optimizer_DevGuide.html). 

### Ready To Use Models

For more information on ready to use deep learning models that have
been converted into the IR format (or include conversion instructions)
please see the the OpenVINO<sup>&#8482;</sup> Toolkit documentation
for
[model_downloader](https://docs.openvinotoolkit.org/latest/omz_tools_downloader_README.html)
and the OpenVINO<sup>&#8482;</sup> Toolkit [Open Model
Zoo](https://github.com/openvinotoolkit/open_model_zoo).

## Model-Proc Files

In addition to the `.xml` and `.bin` files that are part of a model's
`IR` format, `DL Streamer` elements and `FFmpeg Video Analytics`
filters make use of an additional JSON file specifying the input and
output processing instructions for a model. Processing instructions
include details such as the expected color format and resolution of
the input as well labels to associate with a models outputs.

### DL Streamer
For more information on DL Streamer `model-proc` files and samples for
common models please see the DL Streamer
[documentation](https://github.com/opencv/gst-video-analytics/wiki/Model-preparation)
and
[samples](https://github.com/opencv/gst-video-analytics/tree/master/samples/model_proc).

### FFmpeg Video Analytics
For `model-proc` files for use with `FFmpeg Video Analytics` please
see the following [samples](https://github.com/VCDP/FFmpeg-patch/tree/ffmpeg4.2_va/samples/model_proc) 

## How Deep Learning Models are Discovered and Referenced

Model files are stored in a hierarchical directory structure that
determines their name, version and precision.

On startup, the Video Analytics Serving `model_manager` searches
the configured model directory and creates a dictionary storing the
location of each model and their associated collateral
(i.e. `<model-name>.bin`, `<model-name>.xml`, `<model-name>.json`)

The hierarchical directory structure is made up of four levels:

`<model-root-directory>/<model-name>/<version>/<precision>`


Here's a sample directory listing for the `emotion_recognition` model: 

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

## Referencing Models in Pipeline Definitions

Pipeline definitions reference models in their templates in a similar
way to how they reference parameters. Instead of being resolved by
values passed into the pipeline by a request, model paths are resolved
by passing in a dictionary containing information for all models that
have been discovered by the `model_manager` module.

Pipeline templates refer to specific model files using a nested
dictionary and standard Python dictionary indexing with the following
hierarchy: `models[model-name][version][precision][file-type]`.

The default precision for a given model and inference device
(`CPU`:`FP32`,`GPU`:`FP16`,`HDDL`:`FP16`) can also be referenced
without specifying the precision:
`models[model-name][version][file-type]`.

**Examples:**

* `models[emotion_recognition][1][proc]` expands to `emotions-recognition-retail-0003.json`
* If running on CPU `models[emotion_recognition][1][network]` expands to `emotions-recognition-retail-0003.xml`
* Running on GPU `models[emotion_recognition][1][network]` expands to `emotions-recognition-retail-0003-fp16.xml`
* `models[emotion_recognition][1][INT8][network]` expands to `emotions-recognition-retail-0003-int8.xml`

---
\* Other names and brands may be claimed as the property of others.
