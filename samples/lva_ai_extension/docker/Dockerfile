ARG BASE=video-analytics-serving-gstreamer
FROM $BASE

USER root

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y python3-opencv

# Dependencies installed via pip
COPY ./requirements.txt /
RUN pip3 install  --no-cache-dir -r /requirements.txt
RUN rm -f /requirements.txt

RUN mkdir -p /home/video-analytics-serving/samples
COPY ./client       /home/video-analytics-serving/samples/lva_ai_extension/client
COPY ./common       /home/video-analytics-serving/samples/lva_ai_extension/common
COPY ./models       /home/video-analytics-serving/samples/lva_ai_extension/models
COPY ./pipelines    /home/video-analytics-serving/samples/lva_ai_extension/pipelines
COPY ./sampleframes /home/video-analytics-serving/samples/lva_ai_extension/sampleframes
COPY ./server       /home/video-analytics-serving/samples/lva_ai_extension/server

ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving
ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving/samples/lva_ai_extension/common/grpc_autogen

USER vaserving

EXPOSE 5001

#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/server"]
