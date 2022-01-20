'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import json
import requests
import time

TIMEOUT = 120

def get_pipeline_status(instance_url):
    response = requests.get(instance_url, timeout=TIMEOUT)
    status = json.loads(response.text)
    response.close()
    return status

def get_pipeline_state(instance_url, valid_states):
    status = get_pipeline_status(instance_url)
    state = status.get('state')
    if state in valid_states:
        return valid_states.index(state)
    return -1

def get_pipeline_avg_fps(instance_url):
    status = get_pipeline_status(instance_url)
    avg_fps = status.get('avg_fps')
    print("avg_fps: %s", avg_fps)
    return avg_fps

def wait_for_pipeline_status(instance_url, expected_status, valid_states, timeout):
    elapsed_time = 0.0
    sleep_time = 0.25
    if not expected_status in valid_states:
        return False
    expected_state = valid_states.index(expected_status)
    print("Checking {} for status {}".format(instance_url, expected_status))
    state = get_pipeline_state(instance_url, valid_states)
    while state < expected_state and elapsed_time < timeout:
        time.sleep(sleep_time)
        state = get_pipeline_state(instance_url, valid_states)
        elapsed_time = elapsed_time + sleep_time
    return state >= expected_state
