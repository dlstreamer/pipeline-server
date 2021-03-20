# Using Video Analytics Serving Sample Client
These steps walk you through how to launch the sample client that is included in the repository to exercise the VA Serving REST-API. 

## Build the image
Build the container which includes the service and client:
```
~/video-analytics-serving$ ./docker/build.sh
```

## Start the service
Run the container with the temp folder volume mounted to capture results.
```
~/video-analytics-serving$ ./docker/run.sh -v /tmp:/tmp --name vaserving
```

## Running the client
Start a new shell and execute the following command to run vaclient. vaclient will run a pipeline with default parameters
```
~/video-analytics-serving$ ./vaclient/vaclient.sh
```
As the pipeline runs, the status is queried and reported by vaclient:

Pipeline Status:
```json
{
  "avg_fps": 98.11027534513353,
  "elapsed_time": 2.0304791927337646,
  "id": 3,
  "start_time": 1614804737.667221,
  "state": "RUNNING"
}
```

Once the pipeline run has completed, the detection results will be displayed by vaclient.

Detection Result:
```json
{
  "objects": [
    {
      "detection": {
        "bounding_box": {
          "x_max": 0.9018613696098328,
          "x_min": 0.7940059304237366,
          "y_max": 0.8923144340515137,
          "y_min": 0.3036338984966278
        },
        "confidence": 0.6951696872711182,
        "label": "bottle",
        "label_id": 5
      },
      "h": 212,
      "roi_type": "bottle",
      "w": 69,
      "x": 508,
      "y": 109
    }
  ],
  "resolution": {
    "height": 360,
    "width": 640
  },
  "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/bottle-detection.mp4?raw=true",
  "timestamp": 39821229050
}
```
### vaclient Options

#### Explore running new pipelines, passing other sources, destination targets, and other options described in the help function:

```
~/video-analytics-serving$ ./vaclient/vaclient.sh --help
```

    usage: vaclient [-h] [--pipeline PIPELINE] [--version VERSION]  
                    [--source SOURCE] [--destination DESTINATION]  
                    [--repeat REPEAT] [--quiet] [--get_pipelines] 
                    [--get_models]  

    optional arguments:
    -h, --help            show this help message and exit
    --pipeline PIPELINE   One of the supported pipelines you want to launch;
                            e.g., 'object_detection' or 'emotion_recognition'.
                            (default: object_detection)
    --version VERSION     Version associated with the pipeline to launch; e.g.,
                            '1' or '2'. (default: 1)
    --source SOURCE       Location of the content to play/analyze. (default:
                            https://github.com/intel-iot-devkit/sample-
                            videos/blob/master/bottle-detection.mp4?raw=true)
    --destination DESTINATION
                            Output file for storing analysis results. (default:
                            /tmp/results.txt)
    --repeat REPEAT       Number of times to launch this pipeline. (default: 1)
    --quiet               Pass this flag to reduce amount of logging. (default:
                            True)
    --get_pipelines       Pass this flag to get supported pipelines. (default:
                            False)
    --get_models          Pass this flag to get supported models. (default:
                            False)

#### Run the pipeline multiple times and suppress logs:
```
~/video-analytics-serving$ ./vaclient/vaclient.sh --quiet --repeat 3
```

This time you will notice a reduction in logging and sample outputs calculated statistics upon completion. Ex:
```json
{
  "Average": 53.95606659806379,
  "Count": 3,
  "Max": 55.831869705475086,
  "Min": 52.22430268675434,
  "Variance": 3.2691954161506676,
  "value": "avg_fps"
}
{
  "Average": 4.637118577957153,
  "Count": 3,
  "Max": 4.787312269210815,
  "Min": 4.4779980182647705,
  "Variance": 0.023978593194669884,
  "value": "elapsed_time"
}
```

#### Updating pipeline and media source. Run the following command. 
```
~/video-analytics-serving$ ./vaclient/vaclient.sh --pipeline emotion_recognition --source https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female-and-male.mp4?raw=true
```
This time you will see the results updated with emotion recognition specifics:

Detection Result: 
```json
{
  "objects": [
    {
      "detection": {
        "bounding_box": {
          "x_max": 0.8246612548828125,
          "x_min": 0.7025996446609497,
          "y_max": 0.5158947110176086,
          "y_min": 0.18212823569774628
        },
        "confidence": 0.9997547268867493,
        "label": "face",
        "label_id": 1
      },
      "emotion": {
        "label": "neutral",
        "model": {
          "name": "0003_EmoNet_ResNet10"
        }
      },
      "h": 144,
      "roi_type": "face",
      "w": 94,
      "x": 540,
      "y": 79
    },
    {
      "detection": {
        "bounding_box": {
          "x_max": 0.30425453186035156,
          "x_min": 0.19498759508132935,
          "y_max": 0.5343287587165833,
          "y_min": 0.2214517593383789
        },
        "confidence": 0.9936121106147766,
        "label": "face",
        "label_id": 1
      },
      "emotion": {
        "label": "neutral",
        "model": {
          "name": "0003_EmoNet_ResNet10"
        }
      },
      "h": 135,
      "roi_type": "face",
      "w": 84,
      "x": 150,
      "y": 96
    }
  ],
  "resolution": {
    "height": 432,
    "width": 768
  },
  "source": "https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female-and-male.mp4?raw=true",
  "timestamp": 143166666666
}
```

### Clean up
Remember to stop the service container once finished
```
	 # docker kill vaserving
```
