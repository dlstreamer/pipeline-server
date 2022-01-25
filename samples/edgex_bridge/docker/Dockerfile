ARG BASE=dlstreamer-pipeline-server-gstreamer
FROM $BASE

RUN mkdir -p /home/pipeline-server/samples
COPY ./extensions /home/pipeline-server/samples/edgex_bridge/extensions
COPY ./edgex_bridge.py /home/pipeline-server/samples/edgex_bridge/edgex_bridge.py

ENV PYTHONPATH=$PYTHONPATH:/home/pipeline-server
ENV PYTHONPATH=$PYTHONPATH:/home/pipeline-server/samples/edgex_bridge

USER pipeline-server

ENTRYPOINT [ "python3", "/home/pipeline-server/samples/edgex_bridge/edgex_bridge.py"]
