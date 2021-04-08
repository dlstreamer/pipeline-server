'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import time
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
        self._pipeline = pipeline
        self._rtsp_path = pipeline.rtsp_path
        self._rtsp_server = pipeline.rtsp_server
        self._identifier = pipeline.identifier
        self._number_frames = 0
        self._app_src = None
        self._is_audio_pipeline = False
        self._fps = 30
        self._logger = logging.get_logger('GStreamerRtspDestination', is_static=True)
        self._start_time = None
        self._need_data = False

    def _init_stream(self, sample):
        caps = sample.get_caps()
        self._rtsp_server.add_stream(self._identifier, self._rtsp_path, caps, self)
        self._start_time = time.time()

    def on_need_data(self, _src, _):
        self._need_data = True

    def enough_data(self, _):
        self._need_data = False

    def set_app_src(self, app_src, is_audio_pipeline):
        self._app_src = app_src
        self._is_audio_pipeline = is_audio_pipeline

    def _push_buffer(self, buffer):
        if not self._is_audio_pipeline:
            buffer.duration = 1/self._fps * Gst.SECOND
        timestamp = self._number_frames * buffer.duration
        buffer.pts = buffer.dts = int(timestamp)
        retval = self._app_src.emit('push-buffer', buffer)
        self._number_frames += 1
        if retval != Gst.FlowReturn.OK:
            self._logger.debug(
                "Push buffer failed for stream {} with {}".format(self._rtsp_path, retval))

    def process_frame(self, frame):
        # pylint: disable=method-hidden
        self._init_stream(frame)
        self.process_frame = self._process_frame
        self.process_frame(frame)

    def _process_frame(self, frame):
        if self._pipeline.frame_count > 0:
            self._fps = self._pipeline.frame_count / (time.time() - self._start_time)
        if self._need_data:
            self._push_buffer(frame.get_buffer())

    def finish(self):
        if self._app_src:
            self._app_src.end_of_stream()
        if self._rtsp_server:
            self._rtsp_server.remove_stream(self._rtsp_path)
