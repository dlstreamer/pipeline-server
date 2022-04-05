#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
FROM python:3

# Extends: https://gitlab.freedesktop.org/gstreamer/gst-examples/-/blob/master/webrtc/signaling/Dockerfile
WORKDIR /opt/
COPY . /opt/

RUN pip3 install --no-cache-dir --user -r requirements.signaling.txt

CMD python -u ./simple_server.py --disable-ssl
