'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import sys
import json
from os import path
import gi
gi.require_version('Gst', '1.0')  # pylint: disable=wrong-import-position
from gi.repository import Gst
from gstgva import VideoFrame

DETECT_THRESHOLD = 0

Gst.init(sys.argv)

class FrameInfo:

    def __init__(self, metadata_file_path, offset_timestamp=0):
        #Json_objects will contain a list of json objects retrieved from the metadata file
        #Assume that this list will not overload memory
        self.json_objects = []
        self.metadata_file_path = metadata_file_path
        self.offset_timestamp = offset_timestamp

    def load_file(self, file_name):
        if path.exists(file_name):
            json_file = open(file_name, "r")
            lines = json_file.readlines()
            lines = lines[:-1]
            for line in lines:
                data = json.loads(line)
                self.json_objects.append(data)

    def process_frame(self, frame: VideoFrame, _: float = DETECT_THRESHOLD) -> bool:
        print("process frame called")
        if not self.json_objects:
            #list is empty, need to populate it
            self.load_file(self.metadata_file_path)
        print(frame.video_meta().buffer.pts)
        while self.json_objects:
            metadata_pts = self.json_objects[0]["timestamp"] + self.offset_timestamp
            timestamp_difference = abs(frame.video_meta().buffer.pts - metadata_pts)
            # A margin of error of 1000 nanoseconds
            # If the difference is greater than the margin of error:
            #   If frame has a higher pts then the timestamp at the head of the list,
            #   pop the head of the list for being outdated
            #   If frame has a lower pts then the timestamp at the head of the list,
            #   its still possible for the timestamp to come up, so break
            # Otherwise, assume this timestamp at the head of the list is accurate to that frame
            if timestamp_difference > 1000:
                if (frame.video_meta().buffer.pts - metadata_pts) > 0:
                    self.json_objects.pop(0)
                    continue
                break
            detected_objects = self.json_objects[0]["objects"]
            for indv_object in detected_objects:
                frame.add_region(
                    indv_object["detection"]["bounding_box"]["x_min"],
                    indv_object["detection"]["bounding_box"]["y_min"],
                    indv_object["detection"]["bounding_box"]["x_max"] - \
                        indv_object["detection"]["bounding_box"]["x_min"],
                    indv_object["detection"]["bounding_box"]["y_max"] - \
                        indv_object["detection"]["bounding_box"]["y_min"],
                    indv_object["detection"]["label"],
                    indv_object["detection"]["confidence"],
                    True)
            self.json_objects.pop(0)
            break
        return True
