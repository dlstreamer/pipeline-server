## Video Analytics Serving Composition
Here is an example of how to integrate your own application/service so it runs within a Video Analytics Serving container.

### Build Video Analytics Serving

First, let's explore how to build Video Analytics Serving components directly from GitHub. In this example, we will build using GStreamer pipeline types.
Check samples/integration/build.sh for additional details.

```bash
VIDEO_ANALYTICS_SERVING_REPO="https://github.com/intel/video-analytics-serving.git"
sudo docker build ${VIDEO_ANALYTICS_SERVING_REPO} --file Dockerfile.gst -t "video_analytics_serving_gstreamer:latest" $(env | grep -E '_(proxy|REPO|VER)=' | sed 's/^/--build-arg /')
```

### Integrating Your Code

Check samples/Integration/SampleIntegrationDockerfile and samples/integration/docker-entrypoint.sh to understand how to create your Dockerfile.
Replace the <your_application_executable> placeholders found in the SampleIntegrationDockerfile and docker-entrypoint.sh along with any application dependencies as needed to run your_application_executable within the resulting docker container so it runs alongside Video Analytics Serving.

Add your own models and create associated pipeline(s) using the patterns shown within these existing definitions as reference.

#### Pipelines

Sample pipelines are located in the ./pipelines directory. Copy or modify these definitions according to your needs.

#### Models

Sample models available in the ./models directory. Copy or modify these definitions according to your needs.

### Volume mounting pipelines, models directory

The sample pipelines and models are included within the resulting docker image and so are located within the Video Analytics Serving container at runtime.
To dynamically access a set of pipeline/model definitions that are located on your host, launch the Video Analytics Serving container using -v parameter to volume mount these local folders. This will replace and override the pipelines/models found inside the container.

```
sudo docker run -it -e http_proxy=$http_proxy -e https_proxy=$https_proxy -p 8080:8080 -v "$PWD"/models:/models -v "$PWD"/pipelines:/pipelines video_analytics_serving_gstreamer:latest
```
