ARG BASE=video-analytics-serving-runtime
FROM $BASE

USER root

# Dependencies installed via pip
COPY ./requirements.txt /
RUN pip3 install  --no-cache-dir -r /requirements.txt
RUN rm -f /requirements.txt

RUN mkdir -p /home/video-analytics-serving/samples
COPY ./client       /home/video-analytics-serving/samples/ava_ai_extension/client
COPY ./common       /home/video-analytics-serving/samples/ava_ai_extension/common
COPY ./models       /home/video-analytics-serving/samples/ava_ai_extension/models
COPY ./pipelines    /home/video-analytics-serving/samples/ava_ai_extension/pipelines
COPY ./sampleframes /home/video-analytics-serving/samples/ava_ai_extension/sampleframes
COPY ./server       /home/video-analytics-serving/samples/ava_ai_extension/server

ENV MODEL_DIR=/home/video-analytics-serving/samples/ava_ai_extension/models
ENV PIPELINE_DIR=/home/video-analytics-serving/samples/ava_ai_extension/pipelines

ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving
ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving/samples/ava_ai_extension/common/grpc_autogen

USER vaserving

EXPOSE 5001

#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python3", "/home/video-analytics-serving/samples/ava_ai_extension/server"]
