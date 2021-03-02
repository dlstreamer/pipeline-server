'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import requests
import pytest
import urllib
import time
import subprocess
import shlex
import statistics
from tests.common import pipeline_processing

TIMEOUT = 120
HTTP_OK = 200
states = ["QUEUED", "RUNNING", "ABORTED", "COMPLETED"]
turbo_filepath_string = "/sys/devices/system/cpu/intel_pstate/no_turbo"

@pytest.mark.performance
def test_pipeline_performance(service, test_case, test_filename, generate):

    iterations = 1
    va_serving_avg_fps = []
    gst_launch_avg_fps = []

    if "fps_percentage_diff_limit" in test_case:
        fps_percentage_diff_limit = test_case["fps_percentage_diff_limit"]
    else:
        pytest.fail("Required parameter fps_percentage_diff_limit missing")
    if "gst_launch_string" in test_case:
        gst_launch_string = test_case["gst_launch_string"]
    else:
        pytest.fail("Required parameter gst_launch_string missing")
    if "iterations" in test_case:
        iterations = test_case["iterations"]
    try:
        disable_turbo()
        run_gst_pipeline(iterations, gst_launch_string, gst_launch_avg_fps)
        run_vas_pipeline(iterations, va_serving_avg_fps, service, test_case)
        check_results(gst_launch_avg_fps, va_serving_avg_fps, fps_percentage_diff_limit)
    finally:
        enable_turbo()

def run_gst_pipeline(iterations, gst_launch_string, gst_launch_avg_fps):
    for i in range(iterations):
        result = subprocess.run(shlex.split(gst_launch_string), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            gst_launch_avg_fps.append(extract_avg_fps_from_output(result.stdout))
        except:
            print(result.stderr)
            pytest.fail("Unable to get avg_fps from gst-launch command")
        print("Completed gst_launch iteration #{iter}".format(iter=i))

def run_vas_pipeline(iterations, va_serving_avg_fps, service, test_case):

    url = urllib.parse.urljoin(service.host, test_case['path'])
    start_test = test_case["start"]
    for i in range(iterations):
        response = requests.post(url,
                                json=start_test["body"],
                                timeout=TIMEOUT)
        # Check response to POST
        assert response.status_code == HTTP_OK, "Status Code Mismatch"
        instance = int(response.text)
        assert type(instance) == int, "Response Type Mismatch"
        assert instance > 0, "Invalid instance"
        # Check pipeline state transitions
        instance_url = "{}/{}".format(url, instance)
        pipeline_processing.wait_for_pipeline_status(instance_url, "COMPLETED", states, TIMEOUT)
        #   Get avg_fps
        va_serving_avg_fps.append(pipeline_processing.get_pipeline_avg_fps(status_url = instance_url + "/status"))
        print("Completed vas_launch iteration #{iter}".format(iter=i))

def check_results(gst_launch_avg_fps, va_serving_avg_fps, fps_percentage_diff_limit):
    gst_launch_overall_avg_fps = statistics.mean(gst_launch_avg_fps)
    va_serving_overall_avg_fps = statistics.mean(va_serving_avg_fps)
    fps_percentage_diff = abs(va_serving_overall_avg_fps - gst_launch_overall_avg_fps) / gst_launch_overall_avg_fps * 100
    print("va_serving_avg_fps = {}".format(va_serving_overall_avg_fps))
    print("gst_launch_avg_fps = {}".format(gst_launch_overall_avg_fps))
    print("fps_percentage_diff = {}".format(fps_percentage_diff))
    assert fps_percentage_diff < fps_percentage_diff_limit

def extract_avg_fps_from_output(output):
    # Get float value between pre & post
    pre  = b'(average): total='
    post = b' fps'
    result = output.split(pre, 1)[1].split(post, 1)[0]
    avg_fps = float(result)
    assert type(avg_fps) == float, "Unable to get avg_fps from gst-launch command"
    return avg_fps

def disable_turbo():
    disable_turbo_string = "echo \"1\" | sudo tee " + turbo_filepath_string
    subprocess.run(shlex.split(disable_turbo_string), stdout=subprocess.DEVNULL, check=True)
    print("turbo disabled")

def enable_turbo():
    enable_turbo_string = "echo \"0\" | sudo tee " + turbo_filepath_string
    subprocess.run(shlex.split(enable_turbo_string), stdout=subprocess.DEVNULL, check=True)
    print("turbo enabled")
