ARG BASE=intel/dlstreamer-pipeline-server:0.7.1

FROM $BASE

USER root

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y xinetd

RUN pip3 install --upgrade pip --no-cache-dir paho-mqtt==1.5.1

COPY ./cpu-available.sh /usr/bin/cpu-available.sh
RUN chmod +x /usr/bin/cpu-available.sh
RUN echo "cpu-available            3333/tcp" >> /etc/services
COPY ./cpu-available /etc/xinetd.d/cpu-available
RUN chmod 644 /etc/xinetd.d/cpu-available


COPY ./node-id.sh /usr/bin/node-id.sh
RUN chmod +x /usr/bin/node-id.sh
RUN echo "node-id            4444/tcp" >> /etc/services
COPY ./node-id /etc/xinetd.d/node-id
RUN chmod 644 /etc/xinetd.d/node-id

COPY ./entrypoint.sh /home/entrypoint.sh
RUN chmod +x /home/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/home/entrypoint.sh"]