ARG BASE=video-analytics-serving-runtime
FROM $BASE

ARG WORKDIR=/home/edge-ai-extension

USER root

# Dependencies installed via pip
COPY ./requirements.txt /
RUN pip3 install  --no-cache-dir -r /requirements.txt
RUN rm -f /requirements.txt

RUN mkdir -p $WORKDIR

COPY ./client       $WORKDIR/client
COPY ./common       $WORKDIR/common
COPY ./models       $WORKDIR/models
COPY ./pipelines    $WORKDIR/pipelines
COPY ./sampleframes $WORKDIR/sampleframes
COPY ./server       $WORKDIR/server

ENV MODEL_DIR=$WORKDIR/models
ENV PIPELINE_DIR=$WORKDIR/pipelines

ENV PYTHONPATH=$PYTHONPATH:$WORKDIR
ENV PYTHONPATH=$PYTHONPATH:$WORKDIR/common/grpc_autogen

WORKDIR $WORKDIR

ARG USER=vaserving
RUN chown ${USER} -R $WORKDIR
USER ${USER}

EXPOSE 5001

ENTRYPOINT [ "python3", "server"]
