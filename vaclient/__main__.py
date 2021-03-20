#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

from urllib.parse import urljoin
import json
import time
import os
import statistics
import sys
import requests
import template
from arguments import parse_args

VIDEO_ANALYTICS_SERVING = "http://localhost:8080/"
TIMEOUT = 30
SLEEP_FOR_STATUS = 0.5

def get(url):
    try:
        status_response = requests.get(url, timeout=TIMEOUT)
        if status_response.status_code == 200:
            return json.loads(status_response.text)
        print("Got unsuccessful status code: {}".format(status_response.status_code))
    except Exception as error:
        print(error)
    return None

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
                    if line and (len(line.strip()) != 0):
                        print("Detection Result: \n")
                        print_json(json.loads(line))
                except Exception as error:
                    print("Error: '{}'".format(line))
                    print(error)


def wait_for_pipeline(instance_id,
                      pipeline="object_detection",
                      version="1",
                      verbose=True):
    #Await pipeline completion
    status = {"state": "RUNNING"}
    while ((status["state"] is None) or
           (status["state"] == "QUEUED") or
           (status["state"] == "RUNNING")):
        #Fetch status of requested pipeline
        status_url = urljoin(VIDEO_ANALYTICS_SERVING,
                             "/".join(["pipelines",
                                       pipeline,
                                       version,
                                       str(instance_id),
                                       "status"]))
        status = get(status_url)
        if status is None:
            return None
        if verbose:
            print("Pipeline Status:\n")
            print_json(status)
        time.sleep(SLEEP_FOR_STATUS)
    return status

# pylint: disable=too-many-arguments


def start_pipeline(stream_uri,
                   pipeline,
                   destination,
                   version="1",
                   tags=None,
                   parameters=None,
                   verbose=True):
    """Launch requested pipeline"""
    request = template.REQUEST_TEMPLATE
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
                           "pipelines/" + pipeline + "/" + version)
    if verbose:
        print("Starting Pipeline: %s" % (pipeline_url))
    try:
        launch_response = requests.post(
            pipeline_url, json=request, timeout=TIMEOUT)
        if launch_response.status_code == 200:
            instance_id = int(launch_response.text)
            return instance_id
        print("Unsucessful status code {} - {}".format(launch_response.status_code, launch_response.text))
    except Exception as error:
        print(error)
    return None


def print_stats(status, key='avg_fps'):
    """Output pipeline statistics"""
    values = [x[key] for x in status if x and key in x and
              'state' in x and x['state'] == "COMPLETED"]
    if values:
        stats = {"value": key,
                 "Average": statistics.mean(values),
                 "Variance": statistics.variance(values),
                 "Max": max(values),
                 "Min": min(values),
                 "Count": len(status)}
        print_json(stats)
    else:
        print("No results")


def launch_pipeline(options):
    """Launch the set of pipelines defined for startup"""
    print("Launching with options:")
    print(options)
    pipeline_stats = []
    for i in range(options.repeat):
        started_instance_id = start_pipeline(options.source,
                                             options.pipeline,
                                             options.destination,
                                             options.version,
                                             verbose=options.verbose)
        if started_instance_id is None:
            sys.exit(1)
        pipeline_stats.append(wait_for_pipeline(started_instance_id,
                                                options.pipeline,
                                                options.version,
                                                verbose=options.verbose))
        read_detection_results(options.destination,
                               verbose=options.verbose)
        print("Repeating {this_instance}/{total_instances}"
              .format(this_instance=i+1, total_instances=options.repeat))
    if len(pipeline_stats) > 1:  # Requires at least two datapoints
        print_stats(pipeline_stats)  # Output avg_fps
        print_stats(pipeline_stats, key="elapsed_time")

def print_list(item_list):
    for item in item_list:
        print(" - {}/{}".format(item["name"], item["version"]))

def _list(list_name):
    url = urljoin(VIDEO_ANALYTICS_SERVING, list_name)
    response = get(url)
    if response is None:
        print("Got empty response retrieving {}".format(list_name))
        return
    print("Loaded {}:".format(list_name))
    print_list(response)

def list_pipelines():
    _list("pipelines")

def list_models():
    _list("models")


def main():
    """Program entrypoint"""
    try:
        options = parse_args()
    except Exception as error:
        print(error)
        sys.exit(1)
    if options.list_pipelines:
        list_pipelines()
    elif options.list_models:
        list_models()
    else:
        launch_pipeline(options)


if __name__ == "__main__":
    main()
