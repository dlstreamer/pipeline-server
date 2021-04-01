'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

from collections import namedtuple, deque
import time
import gi
gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import Gst
from vaserving.common.utils import logging
from vaserving.app_destination import AppDestination
# pylint: enable=wrong-import-position

RtspSample = namedtuple('RtspSample', ['buffer', 'fps'])
RtspSample.__new__.__defaults__ = (None, None, None)

class GStreamerRtspDestination(AppDestination):

    def __init__(self, request, pipeline):
        AppDestination.__init__(self, request, pipeline)

        request_config = request.get("destination", {})
        dest_config = request_config.get("frame", {})
        cache_len = dest_config.get("cache-length", None)
        self._rtsp_samples = deque([], cache_len)
        self._pipeline = pipeline
        self._rtsp_path = pipeline.rtsp_path
        self._rtsp_server = pipeline.rtsp_server
        self._identifier = pipeline.identifier
        self._number_frames = 0
        self._app_src = None
        self._is_audio_pipeline = False
        self._default_fps = 30
        self._logger = logging.get_logger('GStreamerRtspDestination', is_static=True)
        self._start_time = None

    def _init_stream(self, sample):
        caps = sample.get_caps()
        self._rtsp_server.add_stream(self._identifier, self._rtsp_path, caps, self)
        self._start_time = time.time()

    def on_need_data(self, _src, _):
        self._push_buffers()

    def set_app_src(self, app_src, is_audio_pipeline):
        self._app_src = app_src
        self._is_audio_pipeline = is_audio_pipeline

    def _push_buffers(self):
        while len(self._rtsp_samples) > 0:
            rtsp_sample = self._rtsp_samples.popleft()
            buffer = rtsp_sample.buffer
            if not self._is_audio_pipeline:
                buffer.duration = 1/rtsp_sample.fps * Gst.SECOND
            timestamp = self._number_frames * buffer.duration
            buffer.pts = buffer.dts = int(timestamp)
            retval = self._app_src.emit('push-buffer', buffer)
            self._number_frames += 1
            if retval != Gst.FlowReturn.OK:
                self._logger.debug(
                    "Push buffer failed for stream {} with {}".format(self._rtsp_path, retval))

    def _create_output_item(self, sample):
        buf = sample.get_buffer()
        fps = self._default_fps
        if self._pipeline.frame_count > 0:
            fps = self._pipeline.frame_count / (time.time() - self._start_time)
        return RtspSample(buf, fps)

    def process_frame(self, frame):
        # pylint: disable=method-hidden
        self._init_stream(frame)
        self.process_frame = self._process_frame
        self.process_frame(frame)

    def _process_frame(self, frame):
        self._rtsp_samples.append(self._create_output_item(frame))

    def finish(self):
        if self._app_src:
            self._push_buffers()
        if self._app_src:
            self._app_src.end_of_stream()
        self._rtsp_samples.clear()
        if self._rtsp_server:
            self._rtsp_server.remove_stream(self._rtsp_path)
