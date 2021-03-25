'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

from collections import deque

import gi
gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import Gst
from vaserving.common.utils import logging
from vaserving.app_destination import AppDestination
# pylint: enable=wrong-import-position

class GStreamerRtspDestination(AppDestination):

    def __init__(self, request, pipeline):
        AppDestination.__init__(self, request, pipeline)

        request_config = request.get("destination", {})
        dest_config = request_config.get("frame", {})
        cache_len = dest_config.get("cache-length", None)
        self._rtsp_samples = deque([], cache_len)
        self._rtsp_path = pipeline.rtsp_path
        self._rtsp_server = pipeline.rtsp_server
        self._identifier = pipeline.identifier
        self._number_frames = 0
        self._app_src = None
        self._rtsp_pipeline = None
        self._logger = logging.get_logger(
            'GStreamerRtspDestination', is_static=True)

    def _init_stream(self, sample):
        caps = sample.get_caps()
        self._rtsp_server.add_stream(self._identifier, self._rtsp_path, caps, self)

    def on_need_data(self, _src, _):
        while len(self._rtsp_samples) > 0:
            self._push_buffer(self._rtsp_samples.pop())
            if self._rtsp_pipeline.get_state(0).state != Gst.State.PLAYING:
                break

    def set_src_pipeline(self, app_src, rtsp_pipeline):
        self._app_src = app_src
        self._rtsp_pipeline = rtsp_pipeline

    def _push_buffer(self, buffer):
        timestamp = self._number_frames * buffer.duration
        buffer.pts = buffer.dts = int(timestamp)
        retval = self._app_src.emit('push-buffer', buffer)
        self._number_frames += 1
        if retval != Gst.FlowReturn.OK:
            self._logger.warning(
                "Push buffer failed for stream {} with {}".format(self._rtsp_path, retval))

    def process_frame(self, frame):
        # pylint: disable=method-hidden
        self._init_stream(frame)
        self.process_frame = self._process_frame
        self.process_frame(frame)

    def _process_frame(self, frame):
        self._rtsp_samples.append(frame.get_buffer())

    def finish(self):
        if self._rtsp_pipeline and self._app_src and \
            self._rtsp_pipeline.get_state(0).state == Gst.State.PLAYING:
            for buffer in self._rtsp_samples:
                self._push_buffer(buffer)
        if self._app_src:
            self._app_src.end_of_stream()
        self._rtsp_samples.clear()
        if self._rtsp_server:
            self._rtsp_server.remove_stream(self._rtsp_path)
