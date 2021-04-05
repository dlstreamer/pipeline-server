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
import sys
import requests
from results_watcher import ResultsWatcher

SERVER_ADDRESS = "http://localhost:8080/"
RESPONSE_SUCCESS = 200
TIMEOUT = 30
SLEEP_FOR_STATUS = 0.5
WATCHER_POLL_TIME = 0.01
#nosec skips pybandit hits
REQUEST_TEMPLATE = {
    "source": {
        "uri": "",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "file",
            "path": "/tmp/results.jsonl",  # nosec
            "format": "json-lines"
        }
    }
}

RTSP_TEMPLATE = {
    "frame": {
        "type": "rtsp",
        "path": ""
    }
}

def run(args):
    request = REQUEST_TEMPLATE
    update_request_options(request, args)
    try:
        started_instance_id = start_pipeline(request,
                                             args.pipeline,
                                             verbose=args.verbose,
                                             show_request=args.show_request)
        if started_instance_id is None:
            watcher = None
            sys.exit(1)
        watcher = ResultsWatcher(request['destination']['metadata']['path'])

        watcher.watch()
        print_fps(wait_for_pipeline(started_instance_id,
                                    args.pipeline))
        watcher.stop()
    except KeyboardInterrupt:
        if watcher:
            watcher.stop()
        print()
        if started_instance_id:
            stop_pipeline(args.pipeline, started_instance_id)
            print_fps(wait_for_pipeline(started_instance_id, args.pipeline))

def start(args):
    request = REQUEST_TEMPLATE
    update_request_options(request, args)
    start_pipeline(request,
                   args.pipeline,
                   verbose=args.verbose,
                   show_request=args.show_request)

def stop(args):
    stop_pipeline(args.pipeline, args.instance, args.show_request)
    print_fps(get_pipeline_status(args.pipeline, args.instance))

def wait(args):
    try:
        pipeline_status = get_pipeline_status(args.pipeline, args.instance, args.show_request)
        if pipeline_status is not None and "state" in pipeline_status:
            print(pipeline_status["state"])
        else:
            print("Unable to fetch status")
        print_fps(wait_for_pipeline(args.instance,
                                    args.pipeline))
    except KeyboardInterrupt:
        print()
        stop_pipeline(args.pipeline, args.instance)
        print_fps(wait_for_pipeline(args.instance,
                                    args.pipeline))

def status(args):
    pipeline_status = get_pipeline_status(args.pipeline, args.instance, args.show_request)
    if pipeline_status is not None and "state" in pipeline_status:
        print(pipeline_status["state"])
    else:
        print("Unable to fetch status")

def list_pipelines(args):
    _list("pipelines", args.show_request)

def list_models(args):
    _list("models", args.show_request)

def update_request_options(request,
                           args,
                           tags=None):
    if hasattr(args, 'uri'):
        request["source"]["uri"] = args.uri
    if hasattr(args, 'destination') and args.destination:
        request['destination']['metadata'].update(args.destination)
    if hasattr(args, 'parameters') and args.parameters:
        request["parameters"] = dict(args.parameters)
    if hasattr(args, 'rtsp_path') and args.rtsp_path:
        rtsp_template = RTSP_TEMPLATE
        rtsp_template['frame']['path'] = args.rtsp_path
        request['destination'].update(rtsp_template)
    if tags:
        request["tags"] = tags

def start_pipeline(request,
                   pipeline,
                   verbose=True,
                   show_request=False):
    """Launch requested pipeline"""
    try:
        os.remove(os.path.abspath(request['destination']['metadata']['path']))
    except OSError:
        pass
    if verbose and not show_request:
        print("Starting pipeline...")

    pipeline_url = urljoin(SERVER_ADDRESS,
                           "pipelines/" + pipeline)
    instance_id = post(pipeline_url, request, show_request)
    if instance_id:
        if verbose:
            print("Pipeline running: {}, instance = {}".format(pipeline, instance_id))
        else:
            print(instance_id)
        return instance_id
    if verbose:
        print("Pipeline failed to start")

    return None

def stop_pipeline(pipeline, instance_id, show_request=False):
    if not show_request:
        print("Stopping Pipeline...")
    stop_url = urljoin(SERVER_ADDRESS,
                       "/".join(["pipelines",
                                 pipeline,
                                 str(instance_id)]))
    status_code = delete(stop_url, show_request)
    if status_code == RESPONSE_SUCCESS:
        print("Pipeline stopped")
    else:
        print("Pipeline NOT stopped")

def wait_for_pipeline(instance_id,
                      pipeline):
    #Await pipeline completion
    status = {"state": "RUNNING"}
    while ((status["state"] is None) or
           (status["state"] == "QUEUED") or
           (status["state"] == "RUNNING")):
        #Fetch status of requested pipeline
        status = get_pipeline_status(pipeline,
                                     str(instance_id))
        if status is None:
            return None
        time.sleep(SLEEP_FOR_STATUS)
    return status

def get_pipeline_status(pipeline, instance_id, show_request=False):
    status_url = urljoin(SERVER_ADDRESS,
                         "/".join(["pipelines",
                                   pipeline,
                                   str(instance_id),
                                   "status"]))
    return get(status_url, show_request)

def _list(list_name, show_request=False):
    url = urljoin(SERVER_ADDRESS, list_name)
    response = get(url, show_request)
    if response is None:
        print("Got empty response retrieving {}".format(list_name))
        return
    print_list(response)

def post(url, body, show_request=False):
    try:
        if show_request:
            print('POST {}\nBody:{}'.format(url, body))
            sys.exit(0)
        launch_response = requests.post(url, json=body, timeout=TIMEOUT)
        if launch_response.status_code == RESPONSE_SUCCESS:
            instance_id = int(launch_response.text)
            return instance_id
        print("Got unsuccessful status code: {}".format(launch_response.status_code))
        print(launch_response.text)
    except Exception as error:
        print(error)
    return None

def get(url, show_request=False):
    try:
        if show_request:
            print('GET {}'.format(url))
            sys.exit(0)
        status_response = requests.get(url, timeout=TIMEOUT)
        if status_response.status_code == RESPONSE_SUCCESS:
            return json.loads(status_response.text)
        print("Got unsuccessful status code: {}".format(status_response.status_code))
        print(status_response.text)
    except Exception as error:
        print(error)
    return None

def delete(url, show_request=False):
    try:
        if show_request:
            print('DELETE {}'.format(url))
            sys.exit(0)
        stop_response = requests.delete(url, timeout=TIMEOUT)
        if stop_response.status_code != RESPONSE_SUCCESS:
            print("Unsucessful status code {} - {}".format(stop_response.status_code, stop_response.text))
        return stop_response.status_code
    except Exception as error:
        print(error)
    return None

def print_fps(status):
    if status and 'avg_fps' in status:
        print('avg_fps: {:.2f}'.format(status['avg_fps']))

def print_list(item_list):
    for item in item_list:
        print(" - {}/{}".format(item["name"], item["version"]))
