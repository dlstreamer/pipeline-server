'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import argparse
import json
import os
import time
from queue import Queue

import gi

gi.require_version('Gst', '1.0')
# pylint: disable=wrong-import-position
from gi.repository import Gst
from gstgva.util import gst_buffer_data
from vaserving.gstreamer_app_source import GvaFrameData
from vaserving.vaserving import VAServing
# pylint: enable=wrong-import-position

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))

def parse_args(args=None, program_name="App Source and Destination Sample"):

    parser = argparse.ArgumentParser(prog=program_name, fromfile_prefix_chars='@',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--uri", action="store",
                        dest="input_uri",
                        required=False,
                        default="file:///home/video-analytics-serving/samples/classroom.mp4")

    parser.add_argument("--mode", action="store",
                        dest="source_mode",
                        required=False,
                        choices=["pull", "push"],
                        default="pull")

    parser.add_argument("--pipeline", action="store",
                        dest="pipeline",
                        required=False,
                        default="object_detection")

    parser.add_argument("--version", action="store",
                        dest="pipeline_version",
                        required=False,
                        default="app_src_dst")

    parser.add_argument("--parameters", action="store",
                        dest="parameters",
                        required=False,
                        default=None)

    if (isinstance(args, dict)):
        args = ["--{}={}".format(key, value)
                for key, value in args.items() if value]

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args()
    decode_output = Queue()
    detect_input = Queue()
    detect_output = Queue()
    VAServing.start({'log_level': 'INFO', "ignore_init_errors":True})
    parameters = None
    if args.parameters:
        parameters = json.loads(args.parameters)
    # Start object detection pipeline
    # It will wait until it receives frames via the detect_input queue
    detect_pipeline = VAServing.pipeline(args.pipeline, args.pipeline_version)
    detect_pipeline.start(source={"type": "application",
                                  "class": "GStreamerAppSource",
                                  "input": detect_input,
                                  "mode": args.source_mode},
                          destination={"type": "application",
                                       "class": "GStreamerAppDestination",
                                       "output": detect_output,
                                       "mode": "frames"},
                          parameters=parameters)

    # Start decode only pipeline.
    # Its only purpose is to generate decoded frames to be fed into the object detection pipeline
    decode_pipeline = VAServing.pipeline("video_decode", "app_dst")
    decode_pipeline.start(source={"type":"uri",
                                  "uri": args.input_uri},
                          destination={"type":"application",
                                       "class":"GStreamerAppDestination",
                                       "output":decode_output,
                                       "mode":"frames"})

    # Wait for frame to appear in decode output queue
    sequence_number = 0
    result_count = 0
    end_of_stream = False
    while (not end_of_stream):
        if (not decode_output.empty()):
            decoded_frame = decode_output.get()
            if (decoded_frame):
                with gst_buffer_data(decoded_frame.sample.get_buffer(), Gst.MapFlags.READ) as data:
                    new_sample = GvaFrameData(bytes(data),
                                              decoded_frame.sample.get_caps(),
                                              message={'sequence_number':sequence_number,
                                                       'timestamp':time.time()})
                    detect_input.put(new_sample)
                    sequence_number += 1
            else:
                detect_input.put(None)

        while (not detect_output.empty()):
            results = detect_output.get()
            if (results):
                result_count += 1
            else:
                end_of_stream = True
                break

            if (results.video_frame):
                regions = list(results.video_frame.regions())
                messages = list(results.video_frame.messages())

                timestamp = json.loads(messages[0])

                print("Frame: sequence_number:{} timestamp:{}".format(timestamp["sequence_number"],
                                                                      timestamp["timestamp"]))
                if not regions:
                    print("Nothing detected")

                for region in regions:
                    print("\tDetection: Region = {}, Label = {}".format(region.rect(),
                                                                        region.label()))
                    object_id = region.object_id()
                    if object_id:
                        print("\tTracking: object_id = {}".format(object_id))
                    tensors = list(region.tensors())
                    for tensor in tensors:
                        if not tensor.is_detection():
                            layer_name = tensor["layer_name"]
                            label = tensor["label"]
                            print("\tClassification: {} = {}".format(layer_name, label))
                print()

    print("Received {} results".format(result_count))

    VAServing.stop()
