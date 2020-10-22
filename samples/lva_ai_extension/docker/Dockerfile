ARG BASE=video-analytics-serving-gstreamer
FROM $BASE

USER root

# Install required python packages 
RUN pip3 install numpy requests pyyaml protobuf grpcio

USER vaserving

EXPOSE 5001

COPY server/ /server
COPY client/ /client
COPY grpc_autogen/ /grpc_autogen

ENV PYTHONPATH=$PYTHONPATH:/home/video-analytics-serving
ENV PYTHONPATH=$PYTHONPATH:/grpc_autogen
#ENTRYPOINT [ "/bin/bash" ]
ENTRYPOINT [ "python3", "/server/protocol_server_application.py"]