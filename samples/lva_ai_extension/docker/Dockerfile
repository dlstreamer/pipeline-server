ARG BASE=video-analytics-serving-gstreamer
FROM $BASE

USER root

# Install required python packages 
RUN pip3 install numpy requests pyyaml protobuf grpcio

USER vaserving

EXPOSE 5001

RUN mkdir -p /home/video-analytics-serving/samples
COPY lva_ai_extension /home/video-analytics-serving/samples/lva_ai_extension
ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving
ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving/samples/lva_ai_extension/common/grpc_autogen

#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python3", "/home/video-analytics-serving/samples/lva_ai_extension/server"]

