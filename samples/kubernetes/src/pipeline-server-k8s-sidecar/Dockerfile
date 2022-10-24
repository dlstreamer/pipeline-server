#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FROM python:3.11-rc-slim-bullseye

COPY sidecar.py /app/sidecar.py
COPY requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
CMD ["python3", "/app/sidecar.py"]
