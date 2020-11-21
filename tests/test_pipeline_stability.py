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
import tempfile
from tests.common import results_processing

PAUSE = 0.1

def start_and_run_pipeline(_test_case, pipeline, stability_duration, start_time):
    pipeline.start(_test_case["request"])
    status = pipeline.status()
    transitions = [status]
    while (not status.state.stopped()):
        if (status.state != transitions[-1].state):
            transitions.append(status)
        time.sleep(PAUSE)
        status = pipeline.status()
        if (time.time() - start_time) >= stability_duration:
            pipeline.stop()
            return True
    transitions.append(status)
    assert transitions[0].state == Pipeline.State.QUEUED
    assert transitions[-1].state == Pipeline.State.COMPLETED
    return False

@pytest.mark.stability
def test_pipeline_stability(VAServing, test_case, test_filename, generate, numerical_tolerance, stability_duration):
    duration_met = False
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
    if stability_duration is None and "stability_duration" in _test_case:
        stability_duration = _test_case["stability_duration"]
    elif stability_duration is None:
        stability_duration = 600
    if "relaunch_on_complete" in _test_case:
        relaunch_on_complete = _test_case["relaunch_on_complete"]
    VAServing.start(_test_case["options"])
    start_time = time.time()
    if relaunch_on_complete:
        num_loops = 1
        with tempfile.TemporaryDirectory() as temp_dir:
            while not duration_met:
                _test_case["request"]["destination"]["path"] = temp_dir + "/stability" + \
                    str(num_loops) + ".json"
                pipeline = VAServing.pipeline(_test_case["pipeline"]["name"],
                                              _test_case["pipeline"]["version"])
                results_processing.clear_results(_test_case)
                results = []
                thread = results_processing.get_results_fifo(_test_case, results)
                duration_met = start_and_run_pipeline(_test_case, pipeline,
                                                      stability_duration, start_time)
                if (thread):
                    thread.join()
                elif not duration_met:
                    results_processing.get_results_file(_test_case, results)
                if generate:
                    test_case["result"] = results
                    with open(test_filename+'.generated', "w") as test_output:
                        json.dump(test_case, test_output, indent=4)
                elif not duration_met:
                    assert results_processing.cmp_results(results,
                                                          _test_case["result"],
                                                          numerical_tolerance), \
                                                          "Inference Result Mismatch"
                    num_loops = num_loops + 1
    else:
        pipeline = VAServing.pipeline(_test_case["pipeline"]["name"],
                                      _test_case["pipeline"]["version"])
        duration_met = start_and_run_pipeline(_test_case, pipeline, stability_duration, start_time)
    VAServing.stop()
    assert duration_met
