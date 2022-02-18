# Action Recognition Pipeline

## Purpose

This is a pipeline based on the [DLStreamer gvaactionrecognitionbin](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/Action-Recognition) preview element and supports general purpose action recognition.

## Description

### Pipeline

A detailed description can be found [here](https://github.com/openvinotoolkit/open_model_zoo/tree/master/demos/action_recognition_demo/python#how-it-works).

### Models

A composite model is used, consisting of:

- [action-recognition-0001-encoder](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/action-recognition-0001/action-recognition-0001-encoder)
- [action-recognition-0001-decoder](https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/action-recognition-0001/action-recognition-0001-decoder)

These are based on (400 actions) models for [Kinetics-400 dataset](https://deepmind.com/research/open-source/kinetics).

### Parameters

The key parameters of [DLStreamer gvaactionrecognitionbin](https://github.com/openvinotoolkit/dlstreamer_gst/wiki/Action-Recognition) element are the model and device parameters for each of the encoder and decoder models.

> Note: The inference devices are set to "CPU" by default in pipeline.json as default values in gvaactionrecognitionbin are empty strings.

| Parameter | Definition |
|-----------|------------|
|enc-model|  Path to encoder inference model network file |
|dec-model|  Path to decoder inference model network file |
|enc-device|  Encoder inference device i.e CPU/GPU |
|dec-device|  Decoder inference device i.e CPU/GPU |

### Template

Template is outlined in pipeline.json as follows:
> Note : gvametaconvert requires setting "add-tensor-data=true" as the inference details (label, confidence) determined by gvaactionrecognitionbin is available only inside the tensor data

```json
template : "uridecodebin name=source ! videoconvert ! video/x-raw,format=BGRx",
" ! gvaactionrecognitionbin enc-model={models[action_recognition][encoder][network]} dec-model={models[action_recognition][decoder][network]} model-proc={models[action_recognition][decode[proc]} name=action_recognition",
" ! gvametaconvert add-tensor-data=true name=metaconvert",
" ! gvametapublish name=destination",
" ! appsink name=appsink"]
```

## Output

Below is a sample of the inference results i.e metadata (json format):

```json
{
    "objects": [
        {
            "h": 432,
            "tensors": [
                {
                    "confidence": 0.005000564735382795,
                    "label": "surfing crowd",
                    "label_id": 336,
                    "layer_name": "data",
                    "layout": "ANY",
                    "name": "action",
                    "precision": "UNSPECIFIED"
                }
            ],
            "w": 768,
            "x": 0,
            "y": 0
        }
    ],
    "resolution": {
        "height": 432,
        "width": 768
    },
    "source": "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
    "timestamp": 0
}
```

The corresponding pipeline_client output resembles:

```code
 Timestamp <timestamp>
- <label> (<confidence>)
```

For example:

```code
Starting pipeline action_recognition/general, instance = <uuid>
Timestamp 0
- surfing crowd (0.01)
Timestamp 83333333
- surfing crowd (0.01)
Timestamp 166666666
- surfing crowd (0.01)
Timestamp 250000000
- surfing crowd (0.01)
```

## References

- https://github.com/openvinotoolkit/dlstreamer_gst/wiki/Action-Recognition
- https://github.com/openvinotoolkit/dlstreamer_gst/tree/master/samples/gst_launch/action_recognition
- https://github.com/openvinotoolkit/open_model_zoo/blob/master/demos/action_recognition_demo/python/README.md
- https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/intel/action-recognition-0001