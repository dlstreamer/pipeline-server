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
import sys
from tests.common import pipeline_processing

TIMEOUT = 120
HTTP_OK = 200
states = ["QUEUED", "RUNNING", "ABORTED", "COMPLETED"]
results_output_file = "/home/video-analytics-serving/tests/results/pytest/gstreamer/average_fps.txt"
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
    check_turbo_is_disabled()
    run_gst_pipeline(iterations, gst_launch_string, gst_launch_avg_fps)
    run_vas_pipeline(iterations, va_serving_avg_fps, service, test_case)
    check_results(gst_launch_avg_fps, va_serving_avg_fps, fps_percentage_diff_limit)

def run_gst_pipeline(iterations, gst_launch_string, gst_launch_avg_fps):
    for i in range(iterations):
        start_gst_time = time.time()
        print("Initiating gst_launch iteration #{iter}".format(iter=i), flush=True)
        result = subprocess.run(shlex.split(gst_launch_string), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            gst_launch_avg_fps.append(extract_avg_fps_from_output(result.stdout))
        except:
            print(result.stderr)
            pytest.fail("Unable to get avg_fps from gst-launch command")
        time_elapsed = time.time() - start_gst_time
        print("##teamcity[buildStatisticValue key='gst_launch_duration_iter{}' value='{}']".format(i, round(time_elapsed,3)), flush=True)

def run_vas_pipeline(iterations, va_serving_avg_fps, service, test_case):

    url = urllib.parse.urljoin(service.host, test_case['path'])
    start_test = test_case["start"]
    for i in range(iterations):
        start_vas_time = time.time()
        print("Initiating vas_launch iteration #{iter}".format(iter=i), flush=True)
        response = requests.post(url,
                                json=start_test["body"],
                                timeout=TIMEOUT)
        # Check response to POST
        assert response.status_code == HTTP_OK, "Status Code Mismatch"
        instance = int(response.text)
        assert type(instance) == int, "Response Type Mismatch"
        assert instance > 0, "Invalid instance"
        # Check pipeline state transitions
        instance_url = urllib.parse.urljoin(service.host, "pipelines/status/{}".format(instance))
        pipeline_processing.wait_for_pipeline_status(instance_url, "COMPLETED", states, TIMEOUT)
        #   Get avg_fps
        va_serving_avg_fps.append(pipeline_processing.get_pipeline_avg_fps(instance_url))
        time_elapsed = time.time() - start_vas_time
        print("##teamcity[buildStatisticValue key='va_serving_duration_iter{}' value='{}']".format(i, round(time_elapsed,3)), flush=True)

def check_results(gst_launch_avg_fps, va_serving_avg_fps, fps_percentage_diff_limit):
    gst_launch_overall_avg_fps = statistics.mean(gst_launch_avg_fps)
    va_serving_overall_avg_fps = statistics.mean(va_serving_avg_fps)
    fps_percentage_diff = abs(va_serving_overall_avg_fps - gst_launch_overall_avg_fps) / gst_launch_overall_avg_fps * 100
    print("##teamcity[buildStatisticValue key='va_serving_avg_fps' value='{}']".format(round(va_serving_overall_avg_fps,3)))
    print("##teamcity[buildStatisticValue key='gst_launch_avg_fps' value='{}']".format(round(gst_launch_overall_avg_fps,3)))
    print("##teamcity[buildStatisticValue key='fps_percentage_diff' value='{}']".format(round(fps_percentage_diff,3)))
    try:
        with open(results_output_file, 'a+') as output_file:
            artifact_result = "va_serving_avg_fps={}\n".format(round(va_serving_overall_avg_fps,3)) + \
                              "gst_launch_avg_fps={}\n".format(round(gst_launch_overall_avg_fps,3)) + \
                              "fps_percentage_diff={}\n".format(round(fps_percentage_diff,3))
            output_file.write(artifact_result)
            output_file.flush()
    except OSError:
        print("Could not open file for write {}".format(results_output_file))

    assert fps_percentage_diff < fps_percentage_diff_limit

def extract_avg_fps_from_output(output):
    # Get float value between pre & post
    pre  = b'(average): total='
    post = b' fps'
    result = output.split(pre, 1)[1].split(post, 1)[0]
    avg_fps = float(result)
    assert type(avg_fps) == float, "Unable to get avg_fps from gst-launch command"
    return avg_fps

def check_turbo_is_disabled():
    print("Ensuring turbo is disabled.")
    # Caller responsible to ensure turbo is disabled - see performance ADR for details
    inspect_turbo_cmd = "cat " + turbo_filepath_string
    inspect_turbo_result = subprocess.run(shlex.split(inspect_turbo_cmd), capture_output=True)
    print("inspect_turbo_result.stdout: {}".format(inspect_turbo_result.stdout), flush=True)
    print("inspect_turbo_result.stderr: {}".format(inspect_turbo_result.stderr), flush=True)
    assert inspect_turbo_result.stdout == b'1\n', "Host not prepared for Performance Tests, must have PState no_turbo disabled."
    print("Host meets requirements to run Performance tests.")