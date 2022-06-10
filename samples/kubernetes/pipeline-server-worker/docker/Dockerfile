ARG BASE=intel/dlstreamer-pipeline-server:0.7.2

FROM $BASE

USER root

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y xinetd

RUN pip3 install --upgrade pip --no-cache-dir paho-mqtt==1.5.1

COPY ./fps_health_check.py /usr/bin/fps_health_check.py
RUN chmod +x /usr/bin/fps_health_check.py
RUN echo "fps-health-check            3333/tcp" >> /etc/services
COPY ./fps-health-check /etc/xinetd.d/fps-health-check
RUN chmod 644 /etc/xinetd.d/fps-health-check


COPY ./node-id.sh /usr/bin/node-id.sh
RUN chmod +x /usr/bin/node-id.sh
RUN echo "node-id            4444/tcp" >> /etc/services
COPY ./node-id /etc/xinetd.d/node-id
RUN chmod 644 /etc/xinetd.d/node-id

COPY ./entrypoint.sh /home/entrypoint.sh
RUN chmod +x /home/entrypoint.sh

ENTRYPOINT ["/bin/bash", "/home/entrypoint.sh"]