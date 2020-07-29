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

PAUSE = 0.1

def parse_gstreamer_results(output_file):
    results = []
    for x in output_file:
        if (len(x.strip()) != 0):
            results.append(json.loads(x))
    return results

def parse_ffmpeg_results(output_file):
    results = []
    start_marker = "{\"resolution\":"
    data = output_file.read(len(start_marker))
    while True:
        x = output_file.read(len(start_marker))
        if (x):
            data += x
        else:
            break
        end = data.rfind(start_marker, 1)
        if (end != -1):
            message = data[: end]
            data = data[end:]
            results.append(json.loads(message))
    results.append(json.loads(data))
    return results

def get_results_file(test_case, results):
    if test_case["request"]["destination"]["type"] == "file":
        filename = test_case["request"]["destination"]["path"]
        with open(filename) as results_file:
            if test_case["request"]["destination"]["format"] == "json":
                results.extend(json.load(results_file))
            else:
                if (os.environ["FRAMEWORK"] == "ffmpeg"):
                    parse_func = parse_ffmpeg_results
                else:
                    parse_func = parse_gstreamer_results

                results.extend(parse_func(results_file))

def get_results_fifo(test_case, results):
    if test_case["request"]["destination"]["type"] == "file":
        if "fifo" in test_case["request"]["destination"]["path"]:
            thread = Thread(target=_get_results_fifo, args=[test_case, results])
            thread.start()
            return thread
    return None

def _get_results_fifo(test_case, results):
    fifo_name = test_case["request"]["destination"]["path"]
    os.makedirs(os.path.dirname(fifo_name), exist_ok=True)

    try:
        os.remove(fifo_name)
    except:
        pass

    os.mkfifo(fifo_name)

    fifo = open(fifo_name, "r")

    if (os.environ["FRAMEWORK"] == "ffmpeg"):
        parse_func = parse_ffmpeg_results
    else:
        parse_func = parse_gstreamer_results

    results.extend(parse_func(fifo))
    fifo.close()
    os.remove(fifo_name)

def clear_results(test_case):
    if test_case["request"]["destination"]["type"] == "file":
        try:
            os.remove(test_case["request"]["destination"]["path"])
        except:
            pass

def cmp_results(measured, expected, tolerance):

    if measured == expected:
        return True

    assert type(measured) == type(expected), "Type Comparison Mismatch"

    if isinstance(measured, int) or isinstance(measured, float):
        if expected != 0:
            assert  (abs(measured-expected) / abs(expected)) < tolerance, \
            "Measured Value {} not within tolerance ({}) of Expected Value {}".format(measured, tolerance, expected)
        else:
            assert 1 < tolerance, \
            "Measured Value {} not within tolerance ({}) of Expected Value {}".format(measured, tolerance, expected)

        return True

    if isinstance(measured, list):
        assert len(measured) == len(expected), "List length not equal"

        for measured1, expected1 in zip(measured, expected):
            assert cmp_results(measured1, expected1, tolerance), "List items not equal"
        return True

    if isinstance(measured, dict):
        assert len(measured) == len(expected), "Dictionary length not equal"
        for key in measured:
            assert key in expected, "Dictionary keys not equal"
            if key.endswith("id"):
                assert measured[key] == expected[key], "{} doesn't match".format(key)
                return True
            assert cmp_results(measured[key], expected[key], tolerance), "Dictionaries not equal"
        return True

    assert measured == expected, "Values not equal"
    return True


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

    clear_results(_test_case)

    results = []

    thread = get_results_fifo(_test_case, results)

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
    assert transitions[1].state == Pipeline.State.RUNNING
    assert transitions[-1].state == Pipeline.State.COMPLETED

    VAServing.stop()

    if (thread):
        thread.join()
    else:
        get_results_file(_test_case, results)

    if generate:
        test_case["result"] = results
        with open(test_filename+'.generated', "w") as test_output:
            json.dump(test_case, test_output, indent=4)
    else:
        assert cmp_results(results, _test_case["result"], numerical_tolerance), "Inference Result Mismatch"
