'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import json

from vaserving.vaserving import VAServing

source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__) + "/.."))

request = {
    "source": {
        "uri": "file:///home/video-analytics-serving/samples/classroom.mp4",
        "type": "uri"
    },
    "destination": {
        "type": "file",
        "path": "/home/video-analytics-serving/tests/results.txt",
        "format": "json-lines"
    },
    "tags": {
        "hello": "world",
        "one": "two",
        "object": {
            "hello": 1,
            "world": 2
        }
    }
}


def parse_gstreamer_results(output_file):
    result = []
    with open(output_file) as file:
        for x in file:
            if (len(x.strip()) != 0):
                result.append(json.loads(x))
    return result


def parse_ffmpeg_results(output_file):
    result = []
    with open(output_file) as file:
        start_marker = "{\"resolution\":"
        data = file.read(len(start_marker))
        while True:
            x = file.read(len(start_marker))
            if (x):
                data += x
            else:
                break
            end = data.rfind(start_marker, 1)
            if (end != -1):
                message = data[: end]
                data = data[end:]
                result.append(json.loads(message))
    return result


def test_vaserving():

    print(os.environ["FRAMEWORK"])

    if (os.environ["FRAMEWORK"] == "ffmpeg"):
        parse_func = parse_ffmpeg_results
    else:
        parse_func = parse_gstreamer_results

    pipeline_tests = [("object_detection",
                       1, 'pinwheel.ts', 'object_detection.results.json'),
                      ("emotion_recognition",
                       1, 'classroom.mp4', 'emotion_recognition.results.json')]
    network_preference = "{\"CPU\":\"INT32\"}"
    VAServing.start({'log_level': 'DEBUG',
                     "network_preference": network_preference})

    output_files = []

    for pipeline, version, input_file, output_file in pipeline_tests:
        pipeline = VAServing.pipeline(pipeline, version)
        input_file = "file://{}".format(os.path.abspath(
            os.path.join(source_dir, 'samples', input_file)))
        output_file = "{}".format(os.path.abspath(
            os.path.join(source_dir, 'tests', output_file)))
        if (os.path.exists(output_file)):
            os.remove(output_file)
        output_files.append(output_file)
        pipeline.start(request, source={'uri': input_file}, destination={
            'path': output_file})

    VAServing.wait()

    for pipeline in VAServing.pipeline_instances():
        print(pipeline.name())
        print(pipeline.status().state.name)

    for output_file in output_files:
        results = parse_func(output_file)
        for result in results:
            print(json.dumps(result, indent=2, sort_keys=True), flush=True)

    VAServing.stop()
