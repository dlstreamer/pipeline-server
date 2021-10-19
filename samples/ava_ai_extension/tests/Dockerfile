ARG BASE="video-analytics-serving:0.6.1-dlstreamer-edge-ai-extension"
FROM ${BASE} as video-analytics-serving-ava-tests

USER root

# Dependencies from apt-get
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    python3-dev \
    gcc \
    wget && \
    rm -rf /var/lib/apt/lists/*


# Dependencies installed via pip
COPY ./requirements.tests.txt $HOME
RUN pip3 install  --no-cache-dir -r $HOME/requirements.tests.txt
RUN rm -f $HOME/requirements.tests.txt

COPY . $HOME/tests

RUN wget -O classroom.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/classroom.mp4?raw=true
RUN wget -O person-bicycle-car-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true
RUN wget -O people-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/people-detection.mp4?raw=True
RUN wget --no-proxy -O person-bicycle-car-detection_1920_1080_2min.mp4 https://gitlab.devtools.intel.com/media-analytics-pipeline-zoo/media/-/raw/main/video/person-bicycle-car-detection/person-bicycle-car-detection_1920_1080_2min.mp4?inline=false

ENV COVERAGE_RCFILE=$HOME/tests/config/coveragerc

ARG USER=vaserving
RUN chown ${USER} -R $HOME/tests
USER ${USER}

ENTRYPOINT [ "./tests/entrypoint/pytest.sh" ]
