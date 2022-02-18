'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import math
import json
from threading import Thread
from server.common.utils import logging

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
            thread = Thread(target=_get_results_fifo, args=[test_case, results], daemon=True)
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

    if isinstance(measured, int):
        if expected != 0:
            msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
            assert (abs(measured-expected) / abs(expected) <= math.ceil(tolerance)), \
            msg.format(measured, math.ceil(tolerance), expected)
        else:
            msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
            assert tolerance > 1, \
            msg.format(measured, tolerance, expected)
        return True

    if isinstance(measured, float):
        if expected != 0:
            msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
            assert  (abs(measured-expected) / abs(expected)) < tolerance, \
            msg.format(measured, tolerance, expected)
        else:
            msg = "Measured Value {} not within tolerance ({}) of Expected Value {}"
            assert tolerance > 1, \
            msg.format(measured, tolerance, expected)

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
