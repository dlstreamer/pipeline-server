# Changing Object Detection Models
| [Tutorial Overview](#tutorial-overview) | [Understand Model Formats](#1-understand-model-formats) | [Run Existing Object Detection Pipeline](#2-run-existing-object-detection-pipeline) | [Add New Model](#3-add-new-model) | [Re-build the Image](#4-re-build-the-image) | [Run Pipeline with New Model](#5-run-pipeline-with-new-model) |

VA Serving Object Detection pipelines are customizable. A simple pipeline customization is to use a different model.



## Tutorial Overview

It is assumed that you are familiar with VA Serving [docker operation](building_video_analytics_serving.md) and [pipeline definition files](defining_pipelines.md). It is also assumed that you have python3 installed on your Linux host.

This tutorial consists of the following sections:
1.  Understand model formats
2.  Run existing object detection pipeline
3.  Add a new model and update the pipeline definition to use it
4.  Re-build image to include new model and pipeline
5.  Run the pipeline with the new model

Once you complete this tutorial you should be able to quickly obtain and use a new model in a VA Serving pipeline.

> **Note:** The tutorial assumes use of a GStreamer base image.

## 1. Understand Model Formats
OpenVINO* provides a set of ready to use models from the [Open Model Zoo](https://github.com/opencv/open_model_zoo) (OMZ).
OMZ hosts optimized deep learning models to expedite development of inference applications by using free pre-trained models instead of training your own models.

This tutorial assumes you are using a model from OMZ that has a `model-proc`, which is a file that describes the input and output formats supported by the model along with inference output labels.  For more information see [DL Streamer Model Preparation](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/Model-preparation). A list of supported models can be found in the [DL Streamer repo](https://github.com/openvinotoolkit/dlstreamer_gst/tree/v1.2.1/samples/model_proc).

> **Note:** Model-proc files are optional but they ensure better inference by checking the input video format
and advertising labels that can be used by downstream elements.

VA Serving has a built in tool `model_downloader` that obtains a model from OMZ and converts it to the [Intermediate Representation](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_IR_and_opsets.html) (IR) format required by the OpenVINO* inference engine. The tool also gets the associated `model-proc` file.

The following `object_detection` models and pipelines are included in the Video Analytics Serving library.

| Pipeline Endpoint | Model Name                  | Implementation                     | OMZ Model Name |
| ------------- | --------------------------- | -----------------------------------| -------------- |
| `pipelines/object_detection/1` | SSD with MobileNet                   | Caffe | [mobilenet-ssd](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/mobilenet-ssd) |


## 2. Run Existing Object Detection Pipeline
With the service running, you can start the `object_detection` version `1` pipeline as follows:
```bash
$ samples/sample.py --pipeline object_detection --version 1
<snip>
Pipeline Status:

{
    "avg_fps": 51.38943397312732,
    "elapsed_time": 13.621442317962646,
    "id": 1,
    "start_time": 1609889043.9670591,
    "state": "RUNNING"
}
<snip>
{
	"objects": [{
		"detection": {
			"bounding_box": {
				"x_max": 0.9022353887557983,
				"x_min": 0.7940621376037598,
				"y_max": 0.8917602300643921,
				"y_min": 0.30396613478660583
			},
			"confidence": 0.7093080282211304,
			"label": "bottle",
			"label_id": 5
		},
		"h": 212,
		"roi_type": "bottle",
		"w": 69,
		"x": 508,
		"y": 109
	}],
	"resolution": {
		"height": 360,
		"width": 640
	},
	"source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
	"timestamp": 39553072625
}
```

## 3. Add New Model

This example will show how to update the object detection pipeline to use the [yolo-v2-tiny-tf](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/yolo-v2-tiny-tf/yolo-v2-tiny-tf.md) object detection model.

### Select the model
For this example we are using `yolo-v2-tiny-tf`. We'll use the VA Serving model `alias` feature to make this `object_detection` version `yolo-v2-tiny-tf`.

### Add model to model list
Create a copy of the existing model list file `models_list/models.list.yml`, say `models_list/yolo.yml`, then add an entry for the new object detection model `yolo-v2-tiny-tf`.
```yml
- model: yolo-v2-tiny-tf
  alias: object_detection
  version: yolo-v2-tiny-tf
  precision: [FP16,FP32]
```

### Update Pipeline Definition File to Use New Model
Make a copy of the `object_detection` version `1` pipeline definition file and change the version to `yolo-v2-tiny-tf`.
> **Note:** You can also update the existing version `1` to point to the new model instead of creating a new version.
```
$ cp -r pipelines/gstreamer/object_detection/1 pipelines/gstreamer/object_detection/yolo-v2-tiny-tf
```
The pipeline template is shown below:
```
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert",
            " ! gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection",
            " ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```
We need to change the model references used by the `gvadetect` element to use version `yolo-v2-tiny-tf`.
You can use your favorite editor to do this. The below command makes this change using the `sed` utility program.
```
$ sed -i -e s/\\[1\\]/\\[yolo-v2-tiny-tf\\]/g pipelines/gstreamer/object_detection/yolo-v2-tiny-tf/pipeline.json
```
Now the template will look like this:
```
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert",
            " ! gvadetect model-instance-id=inf0 model={models[object_detection][yolo-v2-tiny-tf][network]} model-proc={models[object_detection][yolo-v2-tiny-tf][proc]} name=detection",
            " ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```

## 4. Re-build the Image
Build the image to include the new model and pipeline that references it.
```
$ docker/build.sh --models models_list/yolo.yml
```
The model will now be in `models` folder in the root of the project:
```
models
└── object_detection
    └── yolo-v2-tiny-tf
        ├── FP16
        │   ├── yolo-v2-tiny-tf.bin
        │   ├── yolo-v2-tiny-tf.mapping
        │   └── yolo-v2-tiny-tf.xml
        ├── FP32
        │   ├── yolo-v2-tiny-tf.bin
        │   ├── yolo-v2-tiny-tf.mapping
        │   └── yolo-v2-tiny-tf.xml
        └── yolo-v2-tiny-tf.json
```

## 5. Run Pipeline with New Model
1. Restart the service to ensure we are using the image with the yolo-v2-tiny-tf model
```
$ docker stop video-analytics-serving-gstreamer
$ docker/run.sh -v /tmp:/tmp
```
2. Check whether the new model and pipeline are loaded
```
$ curl localhost:8080/models | grep yolo
      "model-proc": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json",
        "FP16": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP16/yolo-v2-tiny-tf.xml",
        "FP32": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml"
    "version": "yolo-v2-tiny-tf"
$ curl localhost:8080/pipelines | grep yolo
    "version": "yolo-v2-tiny-tf"
```
3. Start pipeline
Start the `object_detection` version `yolo-v2-tiny-tf` pipeline.
> **Note:** The lower fps is due to a higher complexity model.

```bash
$ samples/sample.py --pipeline object_detection --version yolo-v2-tiny-tf
<snip>
Pipeline Status:

{
    "avg_fps": 31.230446318262235,
    "elapsed_time": 11.111731052398682,
    "id": 1,
    "start_time": 1609896673.4552672,
    "state": "RUNNING"
}

<snip>
{
  "objects": [
    {
      "detection": {
        "bounding_box": {
          "x_max": 0.19180697202682495,
          "x_min": 0.09733753651380539,
          "y_max": 0.8905727863311768,
          "y_min": 0.3062259256839752
        },
        "confidence": 0.6085537075996399,
        "label": "bottle",
        "label_id": 5
      },
      "h": 210,
      "roi_type": "bottle",
      "w": 60,
      "x": 62,
      "y": 110
    },
    {
      "detection": {
        "bounding_box": {
          "x_max": 0.8830730319023132,
          "x_min": 0.7777565121650696,
          "y_max": 0.890160083770752,
          "y_min": 0.3054335117340088
        },
        "confidence": 0.5028868913650513,
        "label": "bottle",
        "label_id": 5
      },
      "h": 211,
      "roi_type": "bottle",
      "w": 67,
      "x": 498,
      "y": 110
    }
  ],
  "resolution": {
    "height": 360,
    "width": 640
  },
  "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottl
e-detection.mp4?raw=true",
  "timestamp": 0
}
```

## Related Links
1. For more information on the [Model Download Tool](../tools/model_downloader/README.md)
2. [Converting models to IR format](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_prepare_model_convert_model_Converting_Model.html)
