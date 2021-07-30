'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import sys
import json
import gi
gi.require_version('Gst', '1.0')  # pylint: disable=wrong-import-position
from gi.repository import Gst
from gstgva import VideoFrame

DETECT_THRESHOLD = 0

Gst.init(sys.argv)

class FrameCounter:

    def __init__(self):
        self.count = 0

    def process_frame(self, frame: VideoFrame) -> bool:
        try:
            if frame.messages():
                message = json.loads(frame.messages()[0])
                frame.remove_message(frame.messages()[0])
                message['frame_id'] = self.count
                frame.add_message(json.dumps(message))
        except json.decoder.JSONDecodeError:
            print("Message could not be converted to JSON")
        self.count = self.count + 1
        return True
