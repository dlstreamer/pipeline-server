'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import json
import requests
import time

TIMEOUT = 120

def get_pipeline_state(status_url, valid_states):
    response = requests.get(status_url, timeout=TIMEOUT)
    status = json.loads(response.text)
    response.close()
    state = status.get('state')
    if state in valid_states:
        print("pipeline_state: %s", state)
        return valid_states.index(state)
    return -1

def get_pipeline_avg_fps(status_url):
    response = requests.get(status_url, timeout=TIMEOUT)
    status = json.loads(response.text)
    response.close()
    avg_fps = status.get('avg_fps')
    print("avg_fps: %s", avg_fps)
    return avg_fps
    
def wait_for_pipeline_status(instance_url, expected_status, valid_states, timeout):
    status_url = instance_url + "/status"
    elapsed_time = 0.0
    sleep_time = 0.25
    if not expected_status in valid_states:
        return False
    expected_state = valid_states.index(expected_status)
    print("%s expecting %s" % (instance_url, expected_status))
    state = get_pipeline_state(status_url, valid_states)
    while state < expected_state and elapsed_time < timeout:
        time.sleep(sleep_time)
        state = get_pipeline_state(status_url, valid_states)
        elapsed_time = elapsed_time + sleep_time
        print("%d %f" % (state, elapsed_time))
    return state >= expected_state
    