'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import requests
from collections import namedtuple
import pytest
import urllib
import time
from vaserving.pipeline import Pipeline
from threading import Thread
import copy
from tests.common import results_processing
from queue import Queue
if os.environ['FRAMEWORK'] == "gstreamer":
    import gi
    from gstgva.util import libgst, gst_buffer_data, GVAJSONMeta
    from gstgva.video_frame import VideoFrame
    # pylint: disable=wrong-import-order, wrong-import-position
    gi.require_version('Gst', '1.0')
    gi.require_version('GstApp', '1.0')
    from gi.repository import Gst, GstApp
    # pylint: enable=wrong-import-order, wrong-import-position
    from vaserving.vaserving import VAServing
    from vaserving.app_source import AppSource
    from vaserving.app_destination import AppDestination
    from vaserving.gstreamer_app_source import GStreamerAppSource
    from vaserving.gstreamer_app_source import GvaFrameData
    from vaserving.gstreamer_app_destination import GStreamerAppDestination


PAUSE = 0.1

def _get_results_app(test_case, results):
    decode_output = Queue()
    detect_input = test_case["request"]["source"]["input"]
    detect_output = test_case["request"]["destination"]["output"]
    decode_cfg = test_case["decode"]
    print(decode_cfg)
    decode_cfg["destination"]["output"] = decode_output
    pipeline = VAServing.pipeline(decode_cfg["pipeline"]["name"],
                                  decode_cfg["pipeline"]["version"])
    pipeline.start(decode_cfg)

    sequence_number = 0
    end_of_stream = False
    while (not end_of_stream):
        if (not decode_output.empty()):
            decoded_frame = decode_output.get()
            if (decoded_frame):
                with gst_buffer_data(decoded_frame.sample.get_buffer(), Gst.MapFlags.READ) as data:
                    new_sample = GvaFrameData(bytes(data),
                                              decoded_frame.sample.get_caps(),
                                              message = {'sequence_number':sequence_number})
                    detect_input.put(new_sample)
                    sequence_number += 1
            else:
                detect_input.put(None)

        while (not detect_output.empty()):
            result = detect_output.get()
            if not result:
                end_of_stream = True
                break

            if (result.video_frame):
                regions = list(result.video_frame.regions())
                messages = list(result.video_frame.messages())
                if regions and len(regions):
                    result_dict = {}
                    result_dict['message'] = json.loads(messages[0])
                    region_results = []
                    for region in regions:
                        region_dict = {}
                        rect = region.rect()
                        region_dict['x'] = rect.x
                        region_dict['y'] = rect.y
                        region_dict['w'] = rect.w
                        region_dict['h'] = rect.h
                        region_dict['label'] = region.label()
                        region_results.append(region_dict)
                    result_dict['regions'] = region_results
                    results.append(result_dict)
                    #print(result_dict)

def get_results_app(test_case, results):
    thread = Thread(target=_get_results_app, args=[test_case, results], daemon=True)
    thread.start()
    return thread

def test_pipeline_execution(VAServing, test_case, test_filename, generate, numerical_tolerance):

    _test_case = copy.deepcopy(test_case)

    test_prefix = os.path.splitext(os.path.basename(test_filename))[0]

    test_model_dir = os.path.join(os.path.dirname(test_filename),
                                   "{0}_models".format(test_prefix))

    test_pipeline_dir = os.path.join(os.path.dirname(test_filename),
                                   "{0}_pipelines".format(test_prefix))

    if "model_dir" not in _test_case["options"]:
        if os.path.isdir(test_model_dir):
            _test_case["options"]["model_dir"] = test_model_dir

    if ("pipeline_dir" not in _test_case["options"]):
        if (os.path.isdir(test_pipeline_dir)):
            _test_case["options"]["pipeline_dir"] = test_pipeline_dir

    if "numerical_tolerance" in _test_case:
        numerical_tolerance = _test_case["numerical_tolerance"]

    VAServing.start(_test_case["options"])

    pipeline = VAServing.pipeline(_test_case["pipeline"]["name"],
                                  _test_case["pipeline"]["version"])

    results_processing.clear_results(_test_case)

    results = []

    src_type = _test_case["request"]["source"]["type"]
    print("src_type = {}".format(src_type))
    if src_type == "uri":
        thread = results_processing.get_results_fifo(_test_case, results)
    elif src_type == "application":
        _test_case["request"]["source"]["input"] = Queue()
        _test_case["request"]["destination"]["output"] = Queue()
        thread = get_results_app(_test_case, results)

    pipeline.start(_test_case["request"])

    status = pipeline.status()
    transitions = [status]
    while (not status.state.stopped()):
        if (status.state != transitions[-1].state):
            transitions.append(status)
        time.sleep(PAUSE)
        status = pipeline.status()
    transitions.append(status)

    assert transitions[0].state == Pipeline.State.QUEUED
    assert transitions[-1].state == Pipeline.State.COMPLETED

    if (thread):
        thread.join()
    else:
        results_processing.get_results_file(_test_case, results)

    VAServing.stop()

    if generate:
        test_case["result"] = results
        with open(test_filename+'.generated', "w") as test_output:
            json.dump(test_case, test_output, indent=4)
    else:
        assert results_processing.cmp_results(results, _test_case["result"], numerical_tolerance), "Inference Result Mismatch"
