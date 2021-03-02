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
from tests.common import pipeline_processing

TIMEOUT = 30
HTTP_OK = 200
states = ["QUEUED", "RUNNING", "ABORTED", "COMPLETED"]
states_negative = ["QUEUED", "ERROR"]

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
    if "check_error" in test_case:
        # Negative tests expect errors before pipeline enters RUNNING
        time.sleep(test_case["check_error"]["delay"])
        state_transition_timeout = float(test_case["check_error"]["timeout"])
        assert pipeline_processing.wait_for_pipeline_status(instance_url, "ERROR", states_negative, 
                                        state_transition_timeout), "Pipeline did not error"
    else:
        state_transition_timeout = float(test_case["check_running"]["timeout"])
        assert pipeline_processing.wait_for_pipeline_status(instance_url, "RUNNING", states, 
                                        state_transition_timeout), "Pipeline did not start"
        state_transition_timeout = float(test_case["check_stopped"]["timeout"])
        if "abort" in test_case:
            time.sleep(test_case["abort"]["delay"])
            response = requests.delete(instance_url, timeout=TIMEOUT)
            assert response.status_code == HTTP_OK, "DELETE Status Code Mismatch"
            assert pipeline_processing.wait_for_pipeline_status(instance_url, "ABORTED", states, 
                                            state_transition_timeout), "Pipeline did not abort"
        else:
            assert pipeline_processing.wait_for_pipeline_status(instance_url, "COMPLETED", states, 
                                            state_transition_timeout), "Pipeline did not complete"
