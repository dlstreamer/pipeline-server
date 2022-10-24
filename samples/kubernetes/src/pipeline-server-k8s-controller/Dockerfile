#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FROM python:3.11-rc-slim-bullseye

COPY controller.py /app/controller.py
COPY kubectl.py /app/kubectl.py
COPY cluster.py /app/cluster.py
COPY xpu.py /app/xpu.py
COPY cluster_watch.py /app/cluster_watch.py
COPY pod.py /app/pod.py
COPY requirements.txt /app/requirements.txt
COPY haproxy-template.cfg /haproxy-template.cfg
COPY controller_server.py /app/controller_server.py
COPY run.sh /app/run.sh

RUN pip3 install -r /app/requirements.txt
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
