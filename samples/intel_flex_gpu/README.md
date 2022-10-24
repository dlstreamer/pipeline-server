# Working with Intel® Data Center GPU Flex Series
This article shows you how to create a pipeline that gets the best out of the Intel® Data Center GPU Flex Series.

> The commands in this sample assume you ae running from the project root.

## Choosing Models
Intel® Data Center GPU Flex Series works best with FP16-INT8 precision models that are not widely available in the [OpenVINO™ Toolkit Open Model Zoo](https://github.com/openvinotoolkit/open_model_zoo), so we'll be using the ssdlite_mobilenet_v2 model from the [Intel® Deep Learning Streamer Pipeline Zoo](https://github.com/dlstreamer/pipeline-zoo-models) model repository.

## Preparing Pipeline
The key to good media analytics performance is keeping data in GPU memory as long as possible to avoid the overhead of moving it to and from system memory. To achieve this, we ensure all the following steps run in GPU memory by using [VAAPI](https://intel.github.io/libva/) for media operations and the [OpenVINO™ Toolkit GPU plugin](https://docs.openvino.ai/latest/openvino_docs_OV_UG_supported_plugins_GPU.html) for inference.
* Video decode
* Video pre-processing
* Inference

### Video Decode
We set the GStreamer caps to `memory:VASurface` to ensure the decoder uses GPU memory.

### Inference Pre-Processing
Set the [gvadetect](https://dlstreamer.github.io/elements/gvadetect.html) pre-process-backend property to `vaapi-surface-sharing` so it use the the vaapi surface created by the decoder to perform the required color space conversion and scaling.

### Inference
Set the inference device to GPU.

### GStreamer Template
When we put this all together we get this partial launch string.
```
decodebin ! video/x-raw(memory:VASurface) ! \
gvadetect model={models[object_detection][ssdlite_mobilenet_v2][FP16-INT8][network]} \
pre-process-backend=vaapi-surface-sharing device=GPU
```

The final pipeline can be found [here](pipelines/object_detection/ssdlite_mobilenet_v2/pipeline.json).

## Build
As we're creating a pipeline tuned for GPU we can't use the reference pipelines so will build an image without pipelines or models.
```
docker/build.sh --base intel/dlstreamer:2022.2.0-ubuntu20-gpu419.40 --tag dlstreamer-pipeline-server:flex --models NONE --pipelines NONE
```

Now we need to get the FP16-INT8 precision model from the Intel(R) Deep Learning Streamer Pipeline Zoo model repository.
```
samples/intel_flex_gpu/get_model.sh
```

## Run
We will start the server with the local model and pipeline then use the pipeline client to issue a request
```
docker/run.sh --models $PWD/samples/intel_flex_gpu/models --pipelines $PWD/samples/intel_flex_gpu/pipelines  -v /tmp:/tmp --image dlstreamer-pipeline-server:flex
```
Now run the client and see a processing rate of just over 400fps.
```
client/pipeline_client.sh run object_detection/ssdlite_mobilenet_v2 https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4
<snip>
Starting pipeline object_detection/ssdlite_mobilenet_v2, instance = 05ee74704b5b11ed93140242ac110002
Pipeline running - instance_id = 05ee74704b5b11ed93140242ac110002
avg_fps: 401.47
Done
```
Intel® Data Center GPU Flex Series can give better performance is batching is used (a number of decoded frames are queued and supplied to GPU at once). Here we set a batch size of 32 and see the processing rate increase to over 1000fps.
```
client/pipeline_client.sh run object_detection/ssdlite_mobilenet_v2 https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4
<snip>
Starting pipeline object_detection/ssdlite_mobilenet_v2, instance = 3c8c3c904c0211eda7dd001b21e5ca0c
Pipeline running - instance_id = 3c8c3c904c0211eda7dd001b21e5ca0c
avg_fps: 1181.43
Done
```
