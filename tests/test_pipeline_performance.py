'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json
import requests
import parse
import pytest
import urllib
import time
import subprocess
import shlex
import statistics
import sys
from parse import search
from tests.common import pipeline_processing

TIMEOUT = 120
HTTP_OK = 200
states = ["QUEUED", "RUNNING", "ABORTED", "COMPLETED"]
results_output_file = "/home/pipeline-server/tests/results/pytest/gstreamer/average_fps.txt"
turbo_filepath_string = "/sys/devices/system/cpu/intel_pstate/no_turbo"

@pytest.mark.performance
def test_pipeline_performance(service, test_case, test_filename, generate):

    iterations = 1
    pipeline_server_avg_fps = []
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
        if iterations < 3:
            pytest.fail("Required parameter iterations must be > 2 to derive the mean")
    check_turbo_is_disabled()
    run_gst_pipeline(iterations, gst_launch_string, gst_launch_avg_fps)
    run_ps_pipeline(iterations, pipeline_server_avg_fps, service, test_case)
    check_results(gst_launch_avg_fps, pipeline_server_avg_fps, fps_percentage_diff_limit)

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

def run_ps_pipeline(iterations, pipeline_server_avg_fps, service, test_case):

    url = urllib.parse.urljoin(service.host, test_case['path'])
    for i in range(iterations):
        start_ps_time = time.time()
        print("Initiating ps_launch iteration #{iter}".format(iter=i), flush=True)
        response = requests.post(url,
                                json=test_case["request"],
                                timeout=TIMEOUT)
        # Check response to POST
        assert response.status_code == HTTP_OK, "Status Code Mismatch"
        instance = json.loads(response.text)
        # Check pipeline state transitions
        instance_url = urllib.parse.urljoin(service.host, "pipelines/status/{}".format(instance))
        pipeline_processing.wait_for_pipeline_status(instance_url, "COMPLETED", states, TIMEOUT)
        #   Get avg_fps
        pipeline_server_avg_fps.append(pipeline_processing.get_pipeline_avg_fps(instance_url))
        time_elapsed = time.time() - start_ps_time
        print("##teamcity[buildStatisticValue key='pipeline_server_duration_iter{}' value='{}']".format(i, round(time_elapsed,3)), flush=True)

def check_results(gst_launch_avg_fps, pipeline_server_avg_fps, fps_percentage_diff_limit):
    print("Excluding gst-launch min value from average fps calculation: {}".format(min(gst_launch_avg_fps)))
    print("Excluding gst-launch max value from average fps calculation: {}".format(max(gst_launch_avg_fps)))
    gst_launch_avg_fps.remove(min(gst_launch_avg_fps))
    gst_launch_avg_fps.remove(max(gst_launch_avg_fps))
    gst_launch_overall_avg_fps = statistics.mean(gst_launch_avg_fps)
    print("Excluding pipeline server min value from average fps calculation: {}".format(min(pipeline_server_avg_fps)))
    print("Excluding pipeline server max value from average fps calculation: {}".format(max(pipeline_server_avg_fps)))
    pipeline_server_avg_fps.remove(min(pipeline_server_avg_fps))
    pipeline_server_avg_fps.remove(max(pipeline_server_avg_fps))
    pipeline_server_overall_avg_fps = statistics.mean(pipeline_server_avg_fps)
    fps_percentage_diff = abs(pipeline_server_overall_avg_fps - gst_launch_overall_avg_fps) / gst_launch_overall_avg_fps * 100
    metrics = {
        "pipeline_server_min_fps" : round(min(pipeline_server_avg_fps),3),
        "pipeline_server_max_fps" : round(max(pipeline_server_avg_fps),3),
        "pipeline_server_avg_fps" : round(pipeline_server_overall_avg_fps,3),
        "gst_launch_min_fps" : round(min(gst_launch_avg_fps),3),
        "gst_launch_max_fps" : round(max(gst_launch_avg_fps),3),
        "gst_launch_avg_fps" : round(gst_launch_overall_avg_fps,3),
        "fps_percentage_diff" : round(fps_percentage_diff,3)
        }
    for key, value in metrics.items():
        print("##teamcity[buildStatisticValue key='{}' value='{}']".format(key, value))

    try:
        with open(results_output_file, 'a+') as output_file:
            artifact_result = "\n".join(["{}={}".format(key, value) for key, value in metrics.items()])
            output_file.write(artifact_result)
            output_file.flush()
    except OSError:
        print("Could not open file for write {}".format(results_output_file))

    assert fps_percentage_diff < fps_percentage_diff_limit

def extract_avg_fps_from_output(output):
    result = search("\nFpsCounter(overall {}sec): total={avg_fps:f} fps, number-streams={}, per-stream={}", output.decode('ascii'))
    avg_fps = result['avg_fps']
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