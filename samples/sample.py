#!/usr/bin/python3
'''
* Copyright (C) 2019 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

from __future__ import print_function
from urllib.parse import urljoin
import argparse
import json
import time
import os
import statistics
import requests

VIDEO_ANALYTICS_SERVING = "http://localhost:8080/pipelines/"
TIMEOUT = 30
SLEEP_FOR_STATUS = 0.5

REQUEST_TEMPLATE = {
    "source": {
        "uri": "file:///home/video-analytics/samples/pinwheel.ts",
        "type": "uri"
    },
    "destination": {
        "path": "/home/video-analytics/samples/results.txt",
        "type": "file",
        "format": "stream"
    }
}

def get_options():
    """Process command line options"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", action="store", dest="pipeline",
                        type="string", default='object_detection')
    parser.add_argument("--source", action="store", dest="source",
                        type="string", default='file:///home/video-analytics/samples/pinwheel.ts')
    parser.add_argument("--destination", action="store", dest="destination",
                        type="string", default='/home/video-analytics/samples/results.txt')
    parser.add_argument("--repeat", action="store", dest="repeat",
                        type="int", default=1)
    parser.add_argument("--quiet", action="store_false", dest="verbose", default=True)

    return parser.parse_args()

def print_json(obj):
    """Output as JSON formatted data"""
    print(json.dumps(obj,
                     sort_keys=True,
                     indent=4,
                     separators=[',', ': ']))

def read_detection_results(destination, verbose=True):
    """Process received detection metadata"""
    if verbose:
        object_lines = []
        with open(destination) as detection_file:
            for line in detection_file:
                try:
                    if line == "{\n":
                        object_lines.append(line)
                        line = None
                    if object_lines:
                        if line:
                            object_lines.append(line)
                        if line == '}\n':
                            line = "".join(object_lines)
                            object_lines = []
                        else:
                            line = None
                    if line:
                        print("Detection Result: \n")
                        print_json(json.loads(line))
                except Exception as error: # pylint: disable=broad-except
                    print(error)

def wait_for_pipeline(instance_id,
                      pipeline="object_detection",
                      version="1",
                      verbose=True):
    """Await pipeline completion"""
    status = {"state":"RUNNING"}
    while ((status["state"] is None) or
           (status["state"] == "QUEUED") or
           (status["state"] == "RUNNING")):
        status = get_status(instance_id, pipeline, version)
        if status is None:
            return None
        if verbose:
            print("Pipeline Status:\n")
            print_json(status)
        time.sleep(SLEEP_FOR_STATUS)
    return status

def get_status(instance_id,
               pipeline="object_detection",
               version="1"):
    """Fetch status of requested pipeline"""
    status_url = urljoin(VIDEO_ANALYTICS_SERVING,
                         "/".join([pipeline,
                                   version,
                                   str(instance_id),
                                   "status"]))
    try:
        status_response = requests.get(status_url, timeout=TIMEOUT)
        if status_response.status_code == 200:
            return json.loads(status_response.text)
    except requests.exceptions.RequestException as request_error:
        print(request_error)
    return None

# pylint: disable=too-many-arguments
def start_pipeline(stream_uri,
                   pipeline,
                   destination,
                   version="1",
                   tags=None,
                   parameters=None,
                   verbose=True):
    """Launch requested pipeline"""
    request = REQUEST_TEMPLATE
    request["source"]["uri"] = stream_uri
    try:
        os.remove(os.path.abspath(destination))
    except OSError:
        pass
    request["destination"]["path"] = os.path.abspath(destination)
    if tags:
        request["tags"] = tags
    if parameters:
        request["parameters"] = parameters
    pipeline_url = urljoin(VIDEO_ANALYTICS_SERVING,
                           pipeline + "/" + version)
    if verbose:
        print("Starting Pipeline: %s" % (pipeline_url))
    try:
        launch_response = requests.post(pipeline_url, json=request, timeout=TIMEOUT)
        if launch_response.status_code == 200:
            instance_id = int(launch_response.text)
            return instance_id
    except requests.exceptions.RequestException as request_error:
        print(request_error)
    return None

def print_stats(status, key='avg_fps'):
    """Output pipeline statistics"""
    values = [x[key] for x in status if x and key in x and
              'state' in x and x['state'] == "COMPLETED"]
    if values:
        stats = {"value":key,
                 "Average":statistics.mean(values),
                 "Variance":statistics.variance(values),
                 "Max":max(values),
                 "Min":min(values),
                 "Count":len(status)}
        print_json(stats)
    else:
        print("No results")

def launch_pipelines(options):
    """Launch the set of pipelines defined for startup"""
    pipeline_status = []
    for i in range(options.repeat):
        started_instance_id = start_pipeline(options.source,
                                             options.pipeline,
                                             options.destination,
                                             verbose=options.verbose)
        pipeline_status.append(wait_for_pipeline(started_instance_id,
                                                 options.pipeline,
                                                 verbose=options.verbose))
        read_detection_results(options.destination,
                               verbose=options.verbose)
        print("Repeating " + str(i) + "/" + options.repeat)
    if pipeline_status:
        print_stats(pipeline_status)
        print_stats(pipeline_status, key="elapsed_time")

if __name__ == "__main__":
    try:
        OPTIONS = get_options()
    except Exception as error: # pylint: disable=broad-except
        print(error)
        exit(1)
    launch_pipelines(OPTIONS)
