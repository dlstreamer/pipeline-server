'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import subprocess
import shlex
import json
import requests
from collections import namedtuple
import pytest
import urllib
import copy
import time
import pytest
from vaserving.pipeline import Pipeline
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

PAUSE = 0.001

def test_pipeline_performance(VAServing, test_case, test_filename, generate):
    iterations = 1
    avg_diff_pct_limit = 10
    start_times_gst_launch = []
    stop_times_gst_launch = []
    start_times_vas_pipeline = []
    stop_times_vas_pipeline = []
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
    if "gst_launch_string" in _test_case:
        gst_launch_string = _test_case["gst_launch_string"]
    else:
        pytest.fail("Required parameter gst_launch_string missing")
    if "iterations" in _test_case:
        iterations = _test_case["iterations"]
    if "avg_diff_pct_limit" in _test_case:
        avg_diff_pct_limit = _test_case["avg_diff_pct_limit"]

    run_gst_pipeline(iterations, start_times_gst_launch, gst_launch_string, stop_times_gst_launch)

    run_vas_pipeline(VAServing, _test_case, iterations,
                     start_times_vas_pipeline,
                     stop_times_vas_pipeline)

    check_results(iterations, stop_times_gst_launch, start_times_gst_launch,
                  stop_times_vas_pipeline, start_times_vas_pipeline,
                  avg_diff_pct_limit)

def run_gst_pipeline(iterations, start_times_gst_launch, gst_launch_string, stop_times_gst_launch):
    for i in range(iterations):
        start_times_gst_launch.append(time.time())
        comp_process = subprocess.run(shlex.split(gst_launch_string))
        stop_times_gst_launch.append(time.time())
        assert comp_process.returncode == 0
        print("Completed gst_launch iteration #{iter}".format(iter=i))

def run_vas_pipeline(VAServing, _test_case, iterations, start_times_vas_pipeline,
                     stop_times_vas_pipeline):
    VAServing.start(_test_case["options"])
    for i in range(iterations):
        pipeline = VAServing.pipeline(_test_case["pipeline"]["name"],
                                      _test_case["pipeline"]["version"])
        start_times_vas_pipeline.append(time.time())
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
        stop_times_vas_pipeline.append(time.time())
        print("Completed vas_launch iteration #{iter}".format(iter=i))
    VAServing.stop()

def check_results(iterations, stop_times_gst_launch, start_times_gst_launch,
                  stop_times_vas_pipeline, start_times_vas_pipeline,
                  avg_diff_pct_limit):
    total_gst_launch = 0
    total_vas_pipeline = 0
    for i in range(iterations):
        total_gst_launch += stop_times_gst_launch[i] - start_times_gst_launch[i]
        total_vas_pipeline += stop_times_vas_pipeline[i] - start_times_vas_pipeline[i]
    avg_duration = total_gst_launch / iterations
    print("avg_duration time = " + str(avg_duration))
    avg_duration_vas = total_vas_pipeline / iterations
    print("avg_duration_vas time = " + str(avg_duration_vas))
    avg_diff_pct = (avg_duration_vas - avg_duration) / avg_duration * 100
    print("avg_diff_pct = " + str(avg_diff_pct))
    assert avg_diff_pct < avg_diff_pct_limit
