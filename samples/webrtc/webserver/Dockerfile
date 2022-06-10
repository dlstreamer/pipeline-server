#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
ARG BASE=nginx:latest

FROM $BASE

# Extends Centricular example found here:
# https://gitlab.freedesktop.org/gstreamer/gst-examples/-/tree/master/webrtc/sendrecv/js

COPY ./www /usr/share/nginx/html

RUN sed -i 's/var default_peer_id;/var default_peer_id = 1;/g' \
    /usr/share/nginx/html/webrtc.js
RUN sed -i 's/wss/ws/g' \
    /usr/share/nginx/html/webrtc.js

USER nginx
