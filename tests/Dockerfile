ARG BASE="video-analytics-serving-gstreamer"
FROM ${BASE} as video-analytics-serving-tests

# Dependencies installed via pip
COPY ./tests/requirements.tests.txt /home/video-analytics-serving
RUN pip3 install  --no-cache-dir -r /home/video-analytics-serving/requirements.tests.txt
RUN rm -f /home/video-analytics-serving/requirements.tests.txt
RUN pip3 list

ARG USER=vaserving

USER ${USER}
