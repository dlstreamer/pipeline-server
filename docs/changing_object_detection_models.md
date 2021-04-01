# Changing Object Detection Models in a Pipeline
| [Background](#background) | [Run Existing Pipeline](#step-1-run-existing-object-detection-pipeline) | [Download New Model](#step-2-download-new-model) | [Create New Pipeline](#step-3-create-new-object-detection-pipeline)
| [Run New Pipeline](#step-4-run-microservice-with-added-model-and-pipeline) | [Rebuild Microservice](#step-6-rebuild-microservice-with-new-model-and-pipeline) | [Further Reading](#further-reading)

Video Analytics Serving pipeline definitions are designed to make
pipeline customization and model selection easy. This tutorial
provides step by step instructions for changing the object detection
reference pipeline to use a different object detection model.

## Models Used:

Original: [mobilenet-ssd](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/mobilenet-ssd/mobilenet-ssd.md)

After Change: [yolo-v2-tiny-tf](https://github.com/openvinotoolkit/open_model_zoo/blob/master/models/public/yolo-v2-tiny-tf/yolo-v2-tiny-tf.md)

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
sample video using the existing `mobilenet-ssd` model.

#### Build the Microservice

Build the sample microservice with the following command:

```bash
./docker/build.sh
```

#### Run the Microservice

Start the sample microservice with the following command:

```bash
./docker/run.sh -v /tmp:/tmp --name vaserving
```

#### Run Interactive Session

In a second terminal window launch an interactive session:

```bash
./docker/run.sh --dev --name vaclient
```

#### Detect Objects on Sample Video

In the interactive session run the sample client to detect objects on
the sample video using version `person_vehicle_bike` of the reference pipeline
`object-detection`.

```bash
./samples/sample.py --pipeline object_detection --version person_vehicle_bike
```

Expected output (abbreviated):
```
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
    "objects": [
        {
            "detection": {
                "bounding_box": {
                    "x_max": 0.16146603226661682,
                    "x_min": 0.11855315417051315,
                    "y_max": 0.3684159517288208,
                    "y_min": 0.30507874488830566
                },
                "confidence": 0.5133300423622131,
                "label": "vehicle",
                "label_id": 2
            },
            "h": 23,
            "roi_type": "vehicle",
            "w": 27,
            "x": 76,
            "y": 110
        }
    ],
    "resolution": {
        "height": 360,
        "width": 640
    },
    "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
    "timestamp": 39050279329
}
```
#### Stop the Microservice

In the original terminal window, stop the service using `CTRL-C`, or in a new terminal window issue a docker kill command:

```bash
docker kill vaserving
```
```bash
docker kill vaclient
```

## Step 2. Download New Model

On start-up Video Analytics Serving discovers models that have been
downloaded and makes them available for reference within pipelines.

Models can be downloaded either as part of the normal Video Analytics
Serving build process or using a stand-alone tool.

#### Add `yolo-v2-tiny-tf` to the Model Downloader List file

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


#### Run Model Downloader

```
./tools/model_downloader/model_downloader.sh --model-list models_list/yolo-models.list.yml
```
Expected output (abbreviated):

```
[ SUCCESS ] Generated IR version 10 model.
[ SUCCESS ] XML file: /tmp/tmp8mq6f1ti/public/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml
[ SUCCESS ] BIN file: /tmp/tmp8mq6f1ti/public/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.bin
[ SUCCESS ] Total execution time: 5.75 seconds.
[ SUCCESS ] Memory consumed: 533 MB.
It's been a while, check for a new version of Intel(R) Distribution of OpenVINO(TM) toolkit here https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit/choose-download.html?cid=other&source=Prod&campid=ww_2020_bu_IOTG_OpenVINO-2021-1&content=upg_pro&medium=organic_uid_agjj or on the GitHub*

Downloaded yolo-v2-tiny-tf model-proc file from gst-video-analytics repo
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

## Step 3. Create New Object Detection Pipeline

#### Copy and Rename Existing Object Detection Pipeline

Make a copy of the `object_detection` version `person_vehicle_bike` pipeline definition file and change the version to `yolo-v2-tiny-tf`.

```
$ cp -r pipelines/gstreamer/object_detection/person_vehicle_bike pipelines/gstreamer/object_detection/yolo-v2-tiny-tf
```

> **Note:** You can also update the existing version `1` to point to the new model instead of creating a new version.

#### Edit the Pipeline Template

Video Analytics Serving pipeline definition files contain a template
that specifies which model to use. The template needs to be updated to
select a different model.

Original pipeline template:

```
"template": ["uridecodebin name=source",
            " ! gvadetect model={models[person_vehicle_bike_detection][1][network]} name=detection",
            " ! gvametaconvert name=metaconvert ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```

We need to change the model references used by the `gvadetect` element to use version `yolo-v2-tiny-tf`.
You can use your favorite editor to do this. The below command makes this change using the `sed` utility program.

```bash
sed -i -e s/\\[1\\]/\\[yolo-v2-tiny-tf\\]/g pipelines/gstreamer/object_detection/yolo-v2-tiny-tf/pipeline.json
```

Edited pipeline template:

```
"template": ["uridecodebin name=source",
            " ! gvadetect model={models[person_vehicle_bike_detection][yolo-v2-tiny-tf][network]} name=detection",
            " ! gvametaconvert name=metaconvert ! gvametapublish name=destination",
            " ! appsink name=appsink"
            ]
```

## Step 4. Run Microservice with Added Model and Pipeline

The sample microservice supports volume mounting of models and
pipelines to make testing local changes easier.

```bash
./docker/run.sh -v /tmp:/tmp --name vaserving --models models --pipelines pipelines/gstreamer
```

Expected output (abbreviated):

```
<snip>
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "==============", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "Loading Models", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "==============", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "Loading Models from Path /home/video-analytics-serving/models", "module": "model_manager"}
{"levelname": "WARNING", "asctime": "2021-01-21 06:58:11,099", "message": "Models directory is mount point", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: audio_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/audio_detection/environment/FP32/aclnet.xml', 'FP16': '/home/video-analytics-serving/models/audio_detection/environment/FP16/aclnet.xml', 'model-proc': '/home/video-analytics-serving/models/audio_detection/environment/aclnet.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: person_vehicle_bike_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/FP32/person-vehicle-bike-detection-crossroad-0078.xml', 'FP16': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/FP16/person-vehicle-bike-detection-crossroad-0078.xml', 'model-proc': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/person-vehicle-bike-detection-crossroad-0078.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: face_detection_retail version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/face_detection_retail/1/FP32/face-detection-retail-0004.xml', 'FP16': '/home/video-analytics-serving/models/face_detection_retail/1/FP16/face-detection-retail-0004.xml', 'model-proc': '/home/video-analytics-serving/models/face_detection_retail/1/face-detection-retail-0004.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: object_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/object_detection/1/FP32/mobilenet-ssd.xml', 'FP16': '/home/video-analytics-serving/models/object_detection/1/FP16/mobilenet-ssd.xml', 'model-proc': '/home/video-analytics-serving/models/object_detection/1/mobilenet-ssd.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: object_detection version: yolo-v2-tiny-tf type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml', 'FP16': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP16/yolo-v2-tiny-tf.xml', 'model-proc': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json'}", "module": "model_manager"}
<snip>
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,549", "message": "Loading Pipeline: object_detection version: yolo-v2-tiny-tf type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/yolo-v2-tiny-tf/pipeline.json", "module": "pipeline_manager"}
```

Once started you can verify that the new model and pipeline have been loaded via `curl`:

```bash
curl localhost:8080/models | grep yolo
```
Expected Output:
```
      "model-proc": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json",
        "FP16": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP16/yolo-v2-tiny-tf.xml",
        "FP32": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml"
    "version": "yolo-v2-tiny-tf"
```
```bash
curl localhost:8080/pipelines | grep yolo
```
Expected Output:
```
    "version": "yolo-v2-tiny-tf"
```

## Step 5. Detect Objects on Sample Video with New Pipeline

#### Run interactive session

In a second terminal window launch an interactive session:

```bash
./docker/run.sh --dev --name vaclient
```

#### Detect Objects on Sample Video

In the interactive session run the sample client to detect objects on
the sample video using version `1` of the reference pipeline
`object-detection`.

```bash
./samples/sample.py --pipeline object_detection --version yolo-v2-tiny-tf
```

Expected output (abbreviated):

```
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

## Step 6. Rebuild Microservice with New Model and Pipeline

Once the new pipeline is ready for deployment you can rebuild the
microservice with the new model and pipeline so it no longer needs to
be volume mounted locally. This step is optional.

```bash
./docker/build.sh --models ./models_list/yolo-models.list.yml --pipelines pipelines/gstreamer
```

Verify the models and pipelines are included:

```bash
./docker/run.sh -v /tmp:/tmp --name vaserving
```

Expected output (abbreviated):

```
<snip>
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "==============", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "Loading Models", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "==============", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,099", "message": "Loading Models from Path /home/video-analytics-serving/models", "module": "model_manager"}
{"levelname": "WARNING", "asctime": "2021-01-21 06:58:11,099", "message": "Models directory is mount point", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: audio_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/audio_detection/environment/FP32/aclnet.xml', 'FP16': '/home/video-analytics-serving/models/audio_detection/environment/FP16/aclnet.xml', 'model-proc': '/home/video-analytics-serving/models/audio_detection/environment/aclnet.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: person_vehicle_bike_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/FP32/person-vehicle-bike-detection-crossroad-0078.xml', 'FP16': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/FP16/person-vehicle-bike-detection-crossroad-0078.xml', 'model-proc': '/home/video-analytics-serving/models/person_vehicle_bike_detection/1/person-vehicle-bike-detection-crossroad-0078.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: face_detection_retail version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/face_detection_retail/1/FP32/face-detection-retail-0004.xml', 'FP16': '/home/video-analytics-serving/models/face_detection_retail/1/FP16/face-detection-retail-0004.xml', 'model-proc': '/home/video-analytics-serving/models/face_detection_retail/1/face-detection-retail-0004.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: object_detection version: 1 type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/object_detection/1/FP32/mobilenet-ssd.xml', 'FP16': '/home/video-analytics-serving/models/object_detection/1/FP16/mobilenet-ssd.xml', 'model-proc': '/home/video-analytics-serving/models/object_detection/1/mobilenet-ssd.json'}", "module": "model_manager"}
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,100", "message": "Loading Model: object_detection version: yolo-v2-tiny-tf type: IntelDLDT from {'FP32': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml', 'FP16': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP16/yolo-v2-tiny-tf.xml', 'model-proc': '/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json'}", "module": "model_manager"}
<snip>
{"levelname": "INFO", "asctime": "2021-01-21 06:58:11,549", "message": "Loading Pipeline: object_detection version: yolo-v2-tiny-tf type: GStreamer from /home/video-analytics-serving/pipelines/object_detection/yolo-v2-tiny-tf/pipeline.json", "module": "pipeline_manager"}
```

Once started you can verify that the new model and pipeline have been loaded via `curl`:

```bash
curl localhost:8080/models | grep yolo
```
Expected Output:
```
"model-proc": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/yolo-v2-tiny-tf.json",
        "FP16": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP16/yolo-v2-tiny-tf.xml",
        "FP32": "/home/video-analytics-serving/models/object_detection/yolo-v2-tiny-tf/FP32/yolo-v2-tiny-tf.xml"
    "version": "yolo-v2-tiny-tf"
```
```bash
curl localhost:8080/pipelines | grep yolo
```
Expected Output:
```
    "version": "yolo-v2-tiny-tf"
```

# Further Reading

For more information on the build, run, pipeline definition and model download please see:

* [Getting Started](/README.md#getting-started)
* [Building Video Analytics Serving](/docs/building_video_analytics_serving.md)
* [Running Video Analytics Serving](/docs/running_video_analytics_serving.md)
* [Defining Pipelines](/docs/defining_pipelines.md)
* [Model Downloader Tool](/tools/model_downloader/README.md)
