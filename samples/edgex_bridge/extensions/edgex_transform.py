'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
import sys
import traceback

import gi

gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import Gst
from gstgva import VideoFrame
from vaserving.common.utils import logging
# pylint: enable=wrong-import-position


def print_message(message):
    print("", flush=True)
    print(message, flush=True)

Gst.init(sys.argv)
logger = logging.get_logger('videoAnalyticsBridge', is_static=True)

class Bridge:  # pylint: disable=too-few-public-methods

    def __init__(self, topic="objects_detected", edgexdevice="videoAnalytics-mqtt",
                 edgexcommand="videoAnalyticsData", edgexresource="videoAnalyticsData"):
        logger.debug('Python Bridge.init() method invoked!')
        self._topic = 'edgex_bridge/' + topic
        self._edgex_device = edgexdevice
        self._edgex_command = edgexcommand
        self._edgex_resource = edgexresource

    def process_frame(self, frame: VideoFrame) -> bool:
        try:
            logger.debug('Python Bridge.process_frame() method invoked!')
            for message in frame.messages():
                frame.remove_message(message)
                msg_dict = {
                    "name":self._edgex_device,
                    "cmd":self._edgex_command,
                    "method":"get",
                    self._edgex_resource:message
                }
                msg_dict = json.dumps(msg_dict)
                frame.add_message(msg_dict)
            logger.debug('Done!')
        except Exception:
            print_message("Error processing frame: {}".format(traceback.print_exc()))
        return True
