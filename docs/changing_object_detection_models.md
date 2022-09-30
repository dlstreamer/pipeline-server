# Changing Object Detection Models in a Pipeline
| [Background](#background)
| [Run Existing Pipeline](#step-1-run-existing-object-detection-pipeline)
| [Download New Model](#step-2-download-new-model)
| [Create New Pipeline](#step-3-create-new-object-detection-pipeline)
| [Run New Pipeline](#step-4-run-microservice-with-added-model-and-pipeline)
| [Rebuild Microservice](#step-6-rebuild-microservice-with-new-model-and-pipeline)
| [Further Reading](#further-reading)

Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server pipeline definitions are designed to make
pipeline customization and model selection easy. This tutorial
provides step by step instructions for changing the object detection
reference pipeline to use a different object detection model.

## Models Used:

Original: [person-vehicle-bike](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/person-vehicle-bike-detection-crossroad-0078)

After Change: [yolo-v2-tiny-tf](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/yolo-v2-tiny-tf)

## Sample Videos Used:

The tutorial uses [bottle-detection.mp4](https://github.com/intel-iot-devkit/sample-videos/raw/master/bottle-detection.mp4)

![bottle-detection.gif](https://github.com/intel-iot-devkit/sample-videos/raw/master/preview/bottle-detection.gif)

# Background

Object detection is a combination of object localization and object
classification. Object detection models take images as input and
produce bounding boxes identifying objects in the image along with
their class or label. Different model architectures and training
datasets have different performance and accuracy characteristics and
it is important to choose the best model for your application.

## Step 1. Run Existing Object Detection Pipeline

Before modifying the pipeline, we'll start by detecting objects in a
sample video using the existing `person-vehicle-bike` model.

### Build and Run the Microservice

Build and run the sample microservice with the following commands:

```bash
./docker/build.sh
./docker/run.sh -v /tmp:/tmp
```

### List Models
Use [pipeline_client](/client/README.md) to list the models. Check that `object_detection/person_vehicle_bike` is present and that that `yolo-v2-tiny-tf` is not. Also count the number of models. In this example there are 7.
```
./client/pipeline_client.sh list-models
```
```
 - audio_detection/environment
 - face_detection_retail/1
 - object_classification/vehicle_attributes
 - object_detection/person_vehicle_bike
 - emotion_recognition/1
```

### Detect Objects on Sample Video
In a second terminal window use [pipeline_client](/client/README.md) to run the pipeline. Expected output is abbreviated.
```bash
./client/pipeline_client.sh run object_detection/person_vehicle_bike https://github.com/intel-iot-devkit/sample-videos/raw/master/bottle-detection.mp4?raw=true
```
```
<snip>
Starting pipeline object_detection/person_vehicle_bike, instance = <uuid>
Timestamp 33519553
- vehicle (0.53) [0.79, 0.71, 0.89, 0.88]
Timestamp 67039106
- vehicle (0.57) [0.79, 0.71, 0.89, 0.88]
Timestamp 100558659
- vehicle (0.51) [0.79, 0.72, 0.89, 0.88]
Timestamp 134078212
- vehicle (0.50) [0.79, 0.71, 0.89, 0.88]
Timestamp 167597765
- vehicle (0.52) [0.79, 0.71, 0.89, 0.88]
Timestamp 201117318
- vehicle (0.52) [0.79, 0.71, 0.89, 0.88]
Timestamp 569832402
- vehicle (0.54) [0.79, 0.71, 0.89, 0.88]
```
You can see that a model trained for vehicles cannot detect bottles.

### Stop the Microservice
In the original terminal window, stop the service using `CTRL-C`.

## Step 2. Download New Model

On start-up the Pipeline Server discovers models that have been
downloaded and makes them available for reference within pipelines.

Models can be downloaded either as part of the normal Pipeline Server build process or using a stand-alone tool.

### Add `yolo-v2-tiny-tf` to the Model Downloader List file

The model downloader tool uses a yml file to specify models to
download along with details on how they will be referenced in
pipelines. The following edits to the file will download
`yolo-v2-tiny-tf` and alias it for reference in pipelines as
`object_detection` version `yolo-v2-tiny-tf`.

Create a copy of the existing model list file `models_list/models.list.yml` and name it `models_list/yolo-models.list.yml`.

```bash
cp ./models_list/models.list.yml ./models_list/yolo-models.list.yml
```

Add an entry for the new object detection model `yolo-v2-tiny-tf` at
the end of the file.

```yml
- model: yolo-v2-tiny-tf
  alias: object_detection
  version: yolo-v2-tiny-tf
  precision: [FP16,FP32]
```

### Run Model Downloader

```
./tools/model_downloader/model_downloader.sh --model-list models_list/yolo-models.list.yml
```
Expected output (abbreviated):

```
[ SUCCESS ] Generated IR version 11 model.
[ SUCCESS ] XML file: /tmp/tmp4u2kd1v9/public/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml
[ SUCCESS ] BIN file: /tmp/tmp4u2kd1v9/public/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.bin
[ SUCCESS ] Total execution time: 3.79 seconds.
[ SUCCESS ] Memory consumed: 532 MB.

Copied model_proc to: /output/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json
```

The model will now be in `models` folder in the root of the project:
> **Note:** If you see an entry for `keras-YOLOv3-model-set` you can ignore it
```
tree models
```
```
models
└── object_detection
    └── yolo-v2-tiny-tf
        ├── coco-80cl.txt
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

## Step 3. Create New Object Detection Pipeline

#### Copy and Rename Existing Object Detection Pipeline

Make a copy of the `object_detection` version `person_vehicle_bike` pipeline definition file and change the version to `yolo-v2-tiny-tf`.

```
cp -r pipelines/gstreamer/object_detection/person_vehicle_bike pipelines/gstreamer/object_detection/yolo-v2-tiny-tf
```

#### Edit the Pipeline Template

The Pipeline Server pipeline definition files contain a template
that specifies which model to use. The template needs to be updated to
select a different model.

Original pipeline template:

```
"template": ["uridecodebin name=source",
            " ! gvadetect model={models[object_detection][person_vehicle_bike][network]} name=detection",
            " ! gvametaconvert name=metaconvert ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```

We need to change the model references used by the `gvadetect` element to use version `yolo-v2-tiny-tf`.
You can use your favorite editor to do this. The below command makes this change using the `sed` utility program.

```bash
sed -i -e s/\\[person_vehicle_bike\\]/\\[yolo-v2-tiny-tf\\]/g pipelines/gstreamer/object_detection/yolo-v2-tiny-tf/pipeline.json
```

Edited pipeline template:

```
"template": ["uridecodebin name=source",
            " ! gvadetect model={models[object_detection][yolo-v2-tiny-tf][network]} name=detection",
            " ! gvametaconvert name=metaconvert ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```

## Step 4. Run Microservice with Added Model and Pipeline

The sample microservice supports volume mounting of models and
pipelines to make testing local changes easier.

```bash
./docker/run.sh -v /tmp:/tmp --models models --pipelines pipelines/gstreamer
```
Once started you can verify that the new model and pipeline have been loaded.

The `list-models` command now shows 8 models, including `object_detection/yolo-v2-tiny-tf`
```bash
./client/pipeline_client.sh list-models
```
```
 - emotion_recognition/1
 - object_detection/yolo-v2-tiny-tf
 - object_detection/person_vehicle_bike
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - face_detection_retail/1
```
The `list-pipelines` command shows `object_detection/yolo-v2-tiny-tf`
```bash
./client/pipeline_client.sh list-pipelines
```
```
 - object_detection/app_src_dst
 - object_detection/yolo-v2-tiny-tf
 - object_detection/object_zone_count
 - object_detection/person_vehicle_bike
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - video_decode/app_dst
 - object_tracking/object_line_crossing
 - object_tracking/person_vehicle_bike
```


## Step 5. Detect Objects on Sample Video with New Pipeline

Now use pipeline_client to run the `object_detection/yolo-v2-tiny-tf` pipeline with the new model.
You can see the `yolo-v2-tiny-tf` model in action as objects are now correctly detected as bottles.
```bash
./client/pipeline_client.sh run object_detection/yolo-v2-tiny-tf https://github.com/intel-iot-devkit/sample-videos/raw/master/bottle-detection.mp4?raw=true
```
```
Pipeline running: object_detection/yolo-v2-tiny-tf, instance = <uuid>
Timestamp 972067039
- bottle (0.51) [0.09, 0.36, 0.18, 0.62]
Timestamp 1005586592
- bottle (0.54) [0.09, 0.37, 0.18, 0.62]
Timestamp 1039106145
- bottle (0.52) [0.09, 0.36, 0.18, 0.62]
Timestamp 1139664804
- bottle (0.50) [0.08, 0.36, 0.18, 0.62]
Timestamp 1206703910
- bottle (0.51) [0.08, 0.36, 0.18, 0.62]
```

## Step 6. Rebuild Microservice with New Model and Pipeline

Once the new pipeline is ready for deployment you can rebuild the
microservice with the new model and pipeline so it no longer needs to
be volume mounted locally.
Delete the `models` folder to avoid accidentally including any cached models created by the model download tool.

```bash
rm -r models
./docker/build.sh --models ./models_list/yolo-models.list.yml
./docker/run.sh -v /tmp:/tmp
```
Once started you can verify that the new model has been loaded.
```bash
./client/pipeline_client.sh list-models
```
```
 - emotion_recognition/1
 - object_detection/yolo-v2-tiny-tf
 - object_detection/person_vehicle_bike
 - object_classification/vehicle_attributes
 - audio_detection/environment
 - face_detection_retail/1
```

# Further Reading

For more information on the build, run, pipeline definition and model download please see:

* [Getting Started](/README.md#getting-started)
* [Building Intel(R) DL Streamer Pipeline Server](/docs/building_pipeline_server.md)
* [Running Intel(R) DL Streamer Pipeline Server](/docs/running_pipeline_server.md)
* [Defining Pipelines](/docs/defining_pipelines.md)
* [Model Downloader Tool](/tools/model_downloader/README.md)
