ARG BASE="video-analytics-serving:0.5.0-dlstreamer-edge-ai-extension"
FROM ${BASE} as video-analytics-serving-lva-tests

USER root

# Dependencies from apt-get
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    python3-dev \
    gcc \
    wget && \
    rm -rf /var/lib/apt/lists/*


# Dependencies installed via pip
COPY ./requirements.tests.txt /home/video-analytics-serving
RUN pip3 install  --no-cache-dir -r /home/video-analytics-serving/requirements.tests.txt
RUN rm -f /home/video-analytics-serving/requirements.tests.txt

COPY . /home/video-analytics-serving/samples/lva_ai_extension/tests

RUN wget -O classroom.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/classroom.mp4?raw=true
RUN wget -O person-bicycle-car-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
RUN wget --no-proxy -O person-bicycle-car-detection_1920_1080_2min.mp4 https://gitlab.devtools.intel.com/media-analytics-pipeline-zoo/media/-/raw/main/video/person-bicycle-car-detection/person-bicycle-car-detection_1920_1080_2min.mp4?inline=false

ARG USER=vaserving

USER ${USER}

WORKDIR /home/video-analytics-serving/samples/lva_ai_extension

ENTRYPOINT [ "pytest", "-s", "--html=tests/results/report.html", "--self-contained-html"]
