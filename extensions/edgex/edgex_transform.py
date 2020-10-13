# ==============================================================================
# Copyright (C) 2018-2020 Intel Corporation
#
# SPDX-License-Identifier: BSD-3-Clause
# ==============================================================================

import sys
import traceback
import gi
from vaserving.common.utils import logging
import json
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
from gstgva import VideoFrame

def print_message(message):
    print("", flush=True)
    print(message, flush=True)

Gst.init(sys.argv)
logger = logging.get_logger('videoAnalyticsBridge', is_static=True)

class Bridge(object):

    def __init__(self, topic="objects_detected", edgexdevice="videoAnalytics-mqtt", edgexcommand="videoAnalyticsData", edgexresource="videoAnalyticsData"):
        logger.debug('Python Bridge.init() method invoked!')
        self._topic = 'edgex_bridge/' + topic
        self._edgexDevice = edgexdevice
        self._edgexCommand = edgexcommand
        self._edgexResource = edgexresource
        
    def process_frame(self, frame: VideoFrame) -> bool:
        try:
            logger.debug('Python Bridge.process_frame() method invoked!')
            for message in frame.messages():
                frame.remove_message(message)
                msg_dict = {
                    "name":self._edgexDevice,
                    "cmd":self._edgexCommand,
                    "method":"get",
                    self._edgexResource: message
                }
                msg_dict = json.dumps(msg_dict)
                frame.add_message(msg_dict)
            logger.debug('Done!')
        except Exception:
            print_message("Error processing frame: {}".format(traceback.print_exc()))
        return True
