ARG BASE="video-analytics-serving-gstreamer"
FROM ${BASE} as video-analytics-serving-tests

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
COPY ./samples/lva_ai_extension/requirements.txt /home/video-analytics-serving/requirements.lva.txt
RUN if [ "$FRAMEWORK" = "gstreamer" ]; then pip3 install  --no-cache-dir -r /home/video-analytics-serving/requirements.lva.txt; fi
RUN rm -f /home/video-analytics-serving/requirements.lva.txt
COPY ./tests/requirements.tests.txt /home/video-analytics-serving
RUN pip3 install  --no-cache-dir -r /home/video-analytics-serving/requirements.tests.txt
RUN rm -f /home/video-analytics-serving/requirements.tests.txt

# Copy tests and sample files
COPY tests/ /home/video-analytics-serving/tests/
COPY samples/ /home/video-analytics-serving/samples/
COPY models_list/models.list.yml /home/video-analytics-serving/models/models.list.yml

# Copy and rename for stringified version

RUN mkdir -p /home/video-analytics-serving/tests/test_cases/pipeline_execution/cpu/object_classification_stringver_cpu_gstreamer_models/object_classification/stringified_version; cp -rf /home/video-analytics-serving/models/object_classification/vehicle_attributes/* /home/video-analytics-serving/tests/test_cases/pipeline_execution/cpu/object_classification_stringver_cpu_gstreamer_models/object_classification/stringified_version

RUN mkdir -p /home/video-analytics-serving/tests/test_cases/pipeline_execution/cpu/object_classification_stringver_cpu_gstreamer_models/object_detection/person_vehicle_bike; cp -rf /home/video-analytics-serving/models/object_detection/person_vehicle_bike/*   /home/video-analytics-serving/tests/test_cases/pipeline_execution/cpu/object_classification_stringver_cpu_gstreamer_models/object_detection/person_vehicle_bike

RUN wget -O tests/media/store-aisle-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/store-aisle-detection.mp4?raw=true
RUN wget -O tests/media/person-bicycle-car-detection.mp4 https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true

ARG USER=vaserving

USER ${USER}

ENTRYPOINT [ "./tests/entrypoint/pytest.sh" ]
