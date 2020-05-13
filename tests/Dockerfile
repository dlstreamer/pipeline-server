ARG BASE="video-analytics-serving-gstreamer"
FROM ${BASE} as video-analytics-serving-tests

USER root

# Dependencies from apt-get
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y -q --no-install-recommends \
    python3-dev \
    gcc && \
    rm -rf /var/lib/apt/lists/*


# Dependencies installed via pip
COPY ./tests/requirements.tests.txt /home/video-analytics-serving
RUN pip3 install  --no-cache-dir -r /home/video-analytics-serving/requirements.tests.txt
RUN rm -f /home/video-analytics-serving/requirements.tests.txt

# Copy tests and sample files
COPY tests/ /home/video-analytics-serving/tests/
COPY samples/ /home/video-analytics-serving/samples/


ARG USER=vaserving

USER ${USER}
