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


TIMEOUT = 30
HTTP_OK = 200
states = [ "QUEUED", "RUNNING", "ABORTED", "COMPLETED" ]

def get_pipeline_state(status_url):
    response = requests.get(status_url, timeout=TIMEOUT)
    status = json.loads(response.text)
    response.close()
    state = status.get('state')
    if state in states:
        return states.index(state)
    else:
        return -1

def wait_for_pipeline_status(instance_url, expected_status, timeout):
    status_url = instance_url + "/status"
    elapsed_time = 0.0
    sleep_time = 0.25
    if not expected_status in states:
        return False
    expected_state = states.index(expected_status)
    print("%s expecting %s" % (instance_url, expected_status))
    state = get_pipeline_state(status_url)
    while state < expected_state and elapsed_time < timeout:
        time.sleep(sleep_time)
        state = get_pipeline_state(status_url)
        elapsed_time = elapsed_time + sleep_time
        print("%d %f" % (state, elapsed_time))
    return state >= expected_state

def test_rest_execution(service, test_case, test_filename, generate):

    url = urllib.parse.urljoin(service.host, test_case['path'])
    start_test = test_case["start"]
    response = requests.post(url,
                            json=start_test["body"],
                            timeout=TIMEOUT)

    if generate:
        test_case["result"] = json.loads(response.text)
        with open(test_filename+'.generated', "w") as test_output:
            json.dump(test_case, test_output, indent=4)
        return

    # Check response to POST
    assert response.status_code == HTTP_OK, "Status Code Mismatch"
    instance = int(response.text)
    assert type(instance) == int, "Response Type Mismatch"    
    assert instance > 0, "Invalid instance"    

    # Check pipeline state transitions
    instance_url = "{}/{}".format(url, instance)
    state_transition_timeout = float(test_case["check_running"]["timeout"])
    assert wait_for_pipeline_status(instance_url, "RUNNING", state_transition_timeout), "Pipeline did not start"
    state_transition_timeout = float(test_case["check_stopped"]["timeout"])
    if "abort" in test_case:
        time.sleep(test_case["abort"]["delay"])
        response = requests.delete(instance_url, timeout=TIMEOUT)
        assert response.status_code == HTTP_OK, "DELETE Status Code Mismatch"
        assert wait_for_pipeline_status(instance_url, "ABORTED", state_transition_timeout), "Pipeline did not abort"
    else:
        assert wait_for_pipeline_status(instance_url, "COMPLETED", state_transition_timeout), "Pipeline did not complete"
