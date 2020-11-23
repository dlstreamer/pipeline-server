ARG BASE="video-analytics-serving:0.4.0-dlstreamer-edge-ai-extension"
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

ENV PIPELINE_NAME 'object_detection'
ENV PIPELINE_VERSION 'person_vehicle_bike_detection'

RUN wget -O classroom.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/classroom.mp4?raw=true

ARG USER=vaserving

USER ${USER}

ENTRYPOINT [ "pytest",  "/home/video-analytics-serving/samples/lva_ai_extension" ]
#ENTRYPOINT [ "/bin/bash" ]
