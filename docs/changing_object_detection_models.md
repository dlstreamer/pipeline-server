# Changing Object Detection Models
| [Tutorial Overview](#tutorial-overview) | [Analyze Existing VAS Object Detection Pipeline](#1-run-existing-vas-object-detection-pipeline) | [Download New Model](#2-download-new-model) | [Update Pipeline Definition File to Use New Model](#3-update-pipeline-definition-file-to-use-new-model) | [Run Pipeline with New Model](#4-run-pipeline-with-new-model) |

VA Serving Object Detection pipelines are customizable. A simple pipeline customization is to use a different model. 

The following `object_detection` models and pipelines are included in the Video Analytics Serving library.  

| Pipeline Endpoint | Model Name                  | Implementation                     | OMZ Model Name | 
| ------------- | --------------------------- | -----------------------------------| -------------- |  
| `pipelines/object_detection/1` | SSD with MobileNet                   | Caffe | [mobilenet-ssd](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/mobilenet-ssd) | 

## Tutorial Overview

This tutorial consists of the following sections:
1.  Analyze the existing VAS Object Detection Model
2.  Download new model
3.  Create/Update the pipeline definition to use the new model
4.  Run the pipeline with the new model
5.  Compare results

Once you complete this tutorial you should be able to quickly obtain, convert and add a new model to the VAS Object Detection Pipeline.

## 1. Run Existing VAS Object Detection Pipeline
With the service running, you can use curl command line program to start the `object_detection` version `1` pipeline included in the VA Serving library as follows:
```bash
$ curl localhost:8080/pipelines/object_detection/1 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results.txt", "format":"json-lines"}}'
```

As the video is being analyzed and as objects appear and disappear you will see detection results in the output file that can be viewed using:

```bash
$ tail -f /tmp/results.txt
```
Pretty printed output below:
```json
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

> **Note:** Currently customization tasks assume use of a GStreamer base image.

## 2. Download New Model
This tutorial is aimed at pipeline customization, not model selection or evaluation. We assume the model is already trained and is known to meet your needs.
This section will show how to obtain a model and update a pipeline description file to use it. 
It is assumed that you are familiar with VA Serving [docker operation](building_video_analytics_serving.md) and [pipeline definition files](defining_pipelines.md).

This example will show how to update the object detection pipeline to use the [yolo-v3-tf](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/yolo-v3-tf/yolo-v3-tf.md) model.

### Start Developer Mode
As this is a development workflow, start the VA Serving container in [developer mode](run_script_reference.md#developer-mode---dev). All subsequent commands will be run in this container.
```
$ docker/run.sh --dev
vaserving@host:~$
```

### Download yolo-v3-tf

OpenVINO* provides a set of ready to use models from the [Open Model Zoo](https://github.com/opencv/open_model_zoo) (OMZ).
OMZ hosts optimized deep learning models to expedite development of inference applications by using free pre-trained models instead of training your own models. 
This tutorial assumes you are using a model from OMZ.

VA Serving has a built in tool `model_downloader` that obtains a model from OMZ and converts it to the [Intermediate Representation](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_IR_and_opsets.html) (IR) format required by the OpenVINO* inference engine. The tool also looks for an associated `model-proc` file that describes the input and output formats supported by the model along with inference output labels. Model-proc files are optional but they ensure better inference by checking the input video format
and advertising labels that can be used by downstream elements. For more information see [DL Streamer Model Preparation](https://github.com/opencv/gst-video-analytics/wiki/Model-preparation).

Follow these steps to get the IR and model-proc files:
1. Select the model, for this example we are using `yolo-v3-tf`. We'll use the VA Serving model `alias` feature to make this `object_detection` version `3`.
2. Create a model list file inside the tools folder, say `yolo.yml` that contains the `model` which is the model name `yolo-v3-tf` in this case, `alias` as `object_detection` and `version` as `3` in yaml file format.

```bash
vaserving@host:~$ echo -e "- model: yolo-v3-tf\n  alias: object_detection\n  version: 3" > tools/yolo.yml
vaserving@host:~$ cat tools/yolo.yml
- model: yolo-v3-tf
  alias: object_detection
  version: 3
```
You can also specify the `precision` you want to download in the yaml file but if none provided it will download all available precisions.

3. Run the model download tool with `yolo.yml` as the input model list file.
```
vaserving@host:~$ python3 tools/model_downloader --model-list tools/yolo.yml --output-dir tools
```

If the tool outputs the below message, it means it has created an empty model-proc file which cannot be referenced by a pipeline element.
```
Warning, model-proc not found in gst-video-analytics repo.
Creating empty json file for <model-name> to allow model to load in VA-Serving
Do not specify model-proc in pipeline that utilizes this model
``` 
We'll need to know this in the [Update/Create Pipeline Definition](#3-update-pipeline-definition-file-to-use-new-model) section.
For this example a model-proc file is available from OMZ.
The model will now be in tools/models folder
```
tools/models
└── object_detection
    └── 3
        ├── FP16
        │   ├── yolo-v3-tf.bin
        │   ├── yolo-v3-tf.mapping
        │   └── yolo-v3-tf.xml
        ├── FP32
        │   ├── yolo-v3-tf.bin
        │   ├── yolo-v3-tf.mapping
        │   └── yolo-v3-tf.xml
        └── yolo-v3-tf.json
```
5. Add this new model to the models folder.
```
vaserving@host:~$ cp -r tools/models/object_detection models
```

## 3. Update Pipeline Definition File to Use New Model
Make a copy of the `object_detection` version `1` pipeline definition file and change the version to `3`.
> **Note:** You can also update the existing version `1` to point to the new model instead of creating a new version.
```
vaserving@host:~$ cp -r pipelines/object_detection/1 pipelines/object_detection/3
```
The pipeline template is shown below:
```
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert",
            " ! gvadetect model-instance-id=inf0 model={models[object_detection][1][network]} model-proc={models[object_detection][1][proc]} name=detection",
            " ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```
We need to change the model references used by the `gvadetect` element to use version `3`. 
You can use your favorite editor to do this. The below command makes this change using the `sed` utility program.
```
vaserving@host:~$ sed -i -e s/\\[1\\]/\\[3\\]/g pipelines/object_detection/3/pipeline.json
``` 
Now the template will look like this:
```
"template": ["urisourcebin name=source ! concat name=c ! decodebin ! video/x-raw ! videoconvert name=videoconvert",
            " ! gvadetect model-instance-id=inf0 model={models[object_detection][3][network]} model-proc={models[object_detection][3][proc]} name=detection",
            " ! gvametaconvert name=metaconvert ! queue ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```
> **Note:** If the download tool reported that it could not find a `model-proc` and created an empty file, we would have to remove the `model-proc` property from the `gvadetect` element. 

## 4. Run Pipeline with New Model
1. Now test the pipeline using the curl commands. We'll run in developer mode so we don't need to re-build the container. 
This means the container will have access to the new model we created but we will have to manually start the service.
```
vaserving@host:~$ python3 -m vaserving
```
2. Check whether the new model is loaded -  
Execute below command to get all model info and search for `yolo`
```
$ curl localhost:8080/models | grep yolo
    "description": "object_detection",
    "name": "object_detection",
      "model-proc": "/home/video-analytics-serving/models/object_detection/3/yolo-v3-tf.json",
        "FP16": "/home/video-analytics-serving/models/object_detection/3/FP16/yolo-v3-tf.xml",
        "FP32": "/home/video-analytics-serving/models/object_detection/3/FP32/yolo-v3-tf.xml"
```
3. Start pipeline -  
Start the `object_detection` version `3` pipeline using the below curl command.
```bash
curl localhost:8080/pipelines/object_detection/3 -X POST -H 'Content-Type: application/json' -d '{ "source": { "uri": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true", "type": "uri" }, "destination": { "type": "file", "path": "/tmp/results2.txt", "format":"json-lines"}}'
```
4. View results in /tmp/results2.txt.
```bash
$ tail -f /tmp/results2.txt
```
Pretty printed output below:
```json
{
	"objects": [{
		"detection": {
			"bounding_box": {
				"x_max": 0.8992204368114471,
				"x_min": 0.7854753136634827,
				"y_max": 0.9538152664899826,
				"y_min": 0.22253309190273285
			},
			"confidence": 0.9900898933410645,
			"label": "bottle",
			"label_id": 39
		},
		"h": 263,
		"roi_type": "bottle",
		"w": 73,
		"x": 503,
		"y": 80
	}, {
		"detection": {
			"bounding_box": {
				"x_max": 0.20874665677547455,
				"x_min": 0.0,
				"y_max": 0.6897994419559836,
				"y_min": 0.004372193478047848
			},
			"confidence": 0.9423678517341614,
			"label": "person",
			"label_id": 0
		},
		"h": 247,
		"roi_type": "person",
		"w": 134,
		"x": 0,
		"y": 2
	}, {
		"detection": {
			"bounding_box": {
				"x_max": 0.19787556678056717,
				"x_min": 0.083109050989151,
				"y_max": 0.9229795336723328,
				"y_min": 0.25158852338790894
			},
			"confidence": 0.8981618285179138,
			"label": "bottle",
			"label_id": 39
		},
		"h": 242,
		"roi_type": "bottle",
		"w": 73,
		"x": 53,
		"y": 91
	}, {
		"detection": {
			"bounding_box": {
				"x_max": 1.0,
				"x_min": 0.0,
				"y_max": 1.0,
				"y_min": 0.6233972907066345
			},
			"confidence": 0.6433367133140564,
			"label": "diningtable",
			"label_id": 60
		},
		"h": 136,
		"roi_type": "diningtable",
		"w": 640,
		"x": 0,
		"y": 224
	}, {
		"detection": {
			"bounding_box": {
				"x_max": 0.5547327473759651,
				"x_min": 0.44895249605178833,
				"y_max": 0.9314501285552979,
				"y_min": 0.24374449253082275
			},
			"confidence": 0.5472988486289978,
			"label": "bottle",
			"label_id": 39
		},
		"h": 248,
		"roi_type": "bottle",
		"w": 68,
		"x": 287,
		"y": 88
	}],
	"resolution": {
		"height": 360,
		"width": 640
	},
	"source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
	"timestamp": 6402234637
}
```

## 5. Compare Results

> **Note:** This section is TBD and will be expanded later.
## Related Links 
1. For more information on the [Model Download Tool](../tools/model_downloader/README.md)
2. [Converting models to IR format](https://docs.openvinotoolkit.org/latest/_docs_MO_DG_prepare_model_convert_model_Converting_Model.html)
