ARG BASE="dlstreamer-pipeline-server-gstreamer"
FROM ${BASE} as dlstreamer-pipeline-server-tests

USER root

# Dependencies from apt-get
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    python3-dev \
    clamav \
    clamav-daemon \
    gcc  \
    wget && \
    rm -rf /var/lib/apt/lists/*


# Dependencies installed via pip
COPY ./tests/requirements.tests.txt /home/pipeline-server
RUN pip3 install  --no-cache-dir -r /home/pipeline-server/requirements.tests.txt
RUN rm -f /home/pipeline-server/requirements.tests.txt

# Copy tests and sample files
COPY tests/ /home/pipeline-server/tests/
COPY samples/ /home/pipeline-server/samples/
COPY models_list/models.list.yml /home/pipeline-server/models/models.list.yml

RUN wget -O tests/media/store-aisle-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/store-aisle-detection.mp4?raw=true
RUN wget -O tests/media/person-bicycle-car-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true

ARG USER=pipeline-server

USER ${USER}

ENTRYPOINT [ "./tests/entrypoint/pytest.sh" ]
