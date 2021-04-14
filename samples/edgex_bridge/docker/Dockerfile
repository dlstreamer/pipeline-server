ARG BASE=video-analytics-serving-gstreamer
FROM $BASE

RUN mkdir -p /home/video-analytics-serving/samples
COPY ./extensions /home/video-analytics-serving/samples/edgex_bridge/extensions
COPY ./edgex_bridge.py /home/video-analytics-serving/samples/edgex_bridge/edgex_bridge.py

ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving
ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving/samples/edgex_bridge

USER vaserving

ENTRYPOINT [ "python3", "/home/video-analytics-serving/samples/edgex_bridge/edgex_bridge.py"]
