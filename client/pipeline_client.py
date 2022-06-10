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
from html.parser import HTMLParser
import requests
import results_watcher
from server.pipeline import Pipeline

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
WEBRTC_TEMPLATE = {
    "frame": {
        "type": "webrtc",
        "peer-id": ""
    }
}

SERVER_CONNECTION_FAILURE_MESSAGE = "Unable to connect to server, check if the pipeline-server microservice is running"

def html_handle_data(self, data):
    self.text += data

HTMLParser.handle_data = html_handle_data

def html_to_text(html: str):
    parser = HTMLParser()
    parser.text = ''
    parser.feed(html)
    return parser.text.strip()

#pylint: disable=too-many-branches
def run(args):
    request = REQUEST_TEMPLATE
    update_request_options(request, args)
    watcher = None
    instance_ids = []
    status_only = args.status_only or args.streams > 1
    try:
        for stream in range(args.streams):
            if status_only:
                print("Starting pipeline {}".format(stream+1))
            try:
                started_instance_id = start_pipeline(args.server_address,
                                                    args.pipeline,
                                                    request,
                                                    verbose=args.verbose,
                                                    show_request=args.show_request)
                instance_ids.append(started_instance_id)
                if wait_for_pipeline_running(args.server_address, started_instance_id):
                    log_pipeline_running(started_instance_id, stream+1, args.verbose, status_only)
                    watcher = start_watcher(request, status_only)
            except Exception as exception:
                if args.streams > 1:
                    print(exception)
                else:
                    raise RuntimeError(exception) from exception
        log_all_pipelines_running(args.streams, len(instance_ids))
        status = wait_for_all_pipeline_completions(args.server_address, instance_ids, status_only=status_only)
        if args.streams == 1:
            print_fps(status)
    except KeyboardInterrupt:
        print()
        for instance_id in instance_ids:
            stop_pipeline(args.server_address, instance_id)
        print_fps(wait_for_all_pipeline_completions(args.server_address, instance_ids))
    except Exception as exception:
        raise RuntimeError(exception) from exception
    finally:
        if watcher:
            watcher.stop()
    print("Done")

def start_watcher(request, status_only):
    watcher = None
    if not status_only:
        error_message = ""
        watcher = results_watcher.create(request)
        if watcher:
            watcher.start()
            if not watcher.watching():
                error_message = watcher.error_message
        if not watcher or not watcher.watching():
            print("No results will be displayed. {}".format(error_message))
    return watcher


def log_pipeline_running(instance_id, stream, verbose, status_only):
    if verbose:
        if status_only:
            print("Pipeline {} running - instance_id = {}".format(stream, instance_id))
        else:
            print("Pipeline running - instance_id = {}".format(instance_id))

def log_all_pipelines_running(num_requested, num_running):
    if num_requested > 1:
        print("{} pipelines running.".format(num_running))

def start(args):
    request = REQUEST_TEMPLATE
    update_request_options(request, args)
    start_pipeline(args.server_address,
                   args.pipeline,
                   request,
                   verbose=args.verbose,
                   show_request=args.show_request)

def stop(args):
    if stop_pipeline(args.server_address, args.instance, args.show_request):
        print_fps([get_pipeline_status(args.server_address, args.instance)])

def wait(args):
    try:
        pipeline_status = get_pipeline_status(args.server_address, args.instance, args.show_request)
        if pipeline_status is not None and "state" in pipeline_status:
            print(pipeline_status["state"])
        else:
            print("Unable to fetch status")
        print_fps([wait_for_pipeline_completion(args.server_address, args.instance)])
    except KeyboardInterrupt:
        print()
        stop_pipeline(args.pipeline, args.instance)
        print_fps([wait_for_pipeline_completion(args.server_address, args.instance)])

def status(args):
    pipeline_status = get_pipeline_status(args.server_address, args.instance, args.show_request)
    if pipeline_status is not None and "state" in pipeline_status:
        print("{} ({}fps)".format(pipeline_status["state"], round(pipeline_status["avg_fps"])))
    else:
        print("Unable to fetch status")

def list_pipelines(args):
    _list(args.server_address, "pipelines", args.show_request)

def list_models(args):
    _list(args.server_address, "models", args.show_request)

def list_instances(args):
    url = urljoin(args.server_address, "pipelines/status")
    statuses = get(url, args.show_request)
    for status in statuses:
        url = urljoin(args.server_address, "pipelines/{}".format(status["id"]))
        response = requests.get(url, timeout=TIMEOUT)
        request_status = json.loads(response.text)
        response.close()
        pipeline = request_status["request"]["pipeline"]
        print("{}: {}/{}".format(status["id"], pipeline["name"], pipeline["version"]))
        print("state: {}".format(status["state"]))
        print("fps: {:.2f}".format(status["avg_fps"]))
        print("source: {}".format(json.dumps(request_status["request"]["source"], indent=4)))
        if request_status["request"].get("destination") is not None:
            print("destination: {}".format(json.dumps(request_status["request"]["destination"], indent=4)))
        if request_status["request"].get("parameters") is not None:
            print("parameters: {}".format(json.dumps(request_status["request"]["parameters"], indent=4)))
        print()

def update_request_options(request,
                           args):
    if hasattr(args, 'uri'):
        request["source"]["uri"] = args.uri
    if hasattr(args, 'destination') and args.destination:
        destination = request['destination']['metadata']
        destination.update(args.destination)
        if destination["type"] != "file":
            del destination["path"]
    if hasattr(args, 'parameters') and args.parameters:
        request["parameters"] = dict(args.parameters)
    if hasattr(args, 'parameter_file') and args.parameter_file:
        with open(args.parameter_file, 'r') as parameter_file:
            parameter_data = json.load(parameter_file)
            if request.get("parameters"):
                request["parameters"].update(parameter_data.get("parameters"))
            else:
                request["parameters"] = parameter_data.get("parameters")
    if hasattr(args, 'tags') and args.tags:
        request["tags"] = dict(args.tags)
    if hasattr(args, 'rtsp_path') and args.rtsp_path:
        rtsp_template = RTSP_TEMPLATE
        rtsp_template['frame']['path'] = args.rtsp_path
        request['destination'].update(rtsp_template)
    if hasattr(args, 'webrtc_peer_id') and args.webrtc_peer_id:
        webrtc_template = WEBRTC_TEMPLATE
        webrtc_template['frame']['peer-id'] = args.webrtc_peer_id
        request['destination'].update(webrtc_template)
    if hasattr(args, 'request_file') and args.request_file:
        with open(args.request_file, 'r') as request_file:
            request.update(json.load(request_file))

def start_pipeline(server_address,
                   pipeline,
                   request,
                   verbose=True,
                   show_request=False):
    """Launch requested pipeline"""
    try:
        if request['destination']['metadata']['type'] == 'file':
            output_file = request['destination']['metadata']['path']
            os.remove(os.path.abspath(output_file))
    except KeyError:
        pass
    except FileNotFoundError:
        pass
    except OSError as error:
        raise OSError("Unable to delete destination metadata file {}".format(output_file)) from error

    pipeline_url = urljoin(server_address, "pipelines/" + pipeline)
    instance_id = post(pipeline_url, request, show_request)
    if instance_id:
        if verbose:
            print("Starting pipeline {}, instance = {}".format(pipeline, instance_id))
        else:
            print(instance_id)
        return instance_id
    if verbose:
        print("Pipeline failed to start")

    return None

def stop_pipeline(server_address, instance_id, show_request=False):
    if not show_request:
        print("Stopping Pipeline...")
    stop_url = urljoin(server_address,
                       "/".join(["pipelines",
                                 str(instance_id)]))
    status_code = delete(stop_url, show_request)
    if status_code == RESPONSE_SUCCESS:
        print("Pipeline stopped")
        return True
    print("Pipeline NOT stopped")
    return False

def wait_for_pipeline_running(server_address,
                              instance_id,
                              timeout_sec = 30):
    status = {"state" : "QUEUED"}
    timeout_count = 0
    while status and not Pipeline.State[status["state"]] == Pipeline.State.RUNNING:
        status = get_pipeline_status(server_address, instance_id)
        if not status or Pipeline.State[status["state"]].stopped():
            break
        time.sleep(SLEEP_FOR_STATUS)
        timeout_count += 1
        if timeout_count * SLEEP_FOR_STATUS >= timeout_sec:
            print("Timed out waiting for RUNNING status")
            break
    if not status or status["state"] == "ERROR":
        raise ValueError("Error in pipeline, please check pipeline-server log messages")
    return Pipeline.State[status["state"]] == Pipeline.State.RUNNING

def wait_for_pipeline_completion(server_address, instance_id):
    status = {"state" : "RUNNING"}
    while status and not Pipeline.State[status["state"]].stopped():
        status = get_pipeline_status(server_address, instance_id)
        time.sleep(SLEEP_FOR_STATUS)
    if status and status["state"] == "ERROR":
        raise ValueError("Error in pipeline, please check pipeline-server log messages")

    return status

def wait_for_all_pipeline_completions(server_address, instance_ids, status_only=False):
    status = {"state" : "RUNNING"}
    status_list = []
    stopped = False
    num_streams = len(instance_ids)
    if num_streams == 0:
        return None
    while status and not stopped:
        if num_streams > 1 or status_only:
            time.sleep(10 * SLEEP_FOR_STATUS)
            all_streams_stopped = True
            first_pipeline = True
            for instance_id in instance_ids:
                status = get_pipeline_status(server_address, instance_id)
                if status:
                    if first_pipeline:
                        print("Pipeline status @ {}s".format(round(status["elapsed_time"])))
                    print("- instance={}, state={}, {}fps".format(
                        instance_id, status["state"], round(status["avg_fps"])))
                    if not Pipeline.State[status["state"]].stopped():
                        all_streams_stopped = False
                    status_list.append(status)
                first_pipeline = False
            stopped = all_streams_stopped
        else:
            time.sleep(SLEEP_FOR_STATUS)
            status = get_pipeline_status(server_address, instance_ids[0])
            stopped = Pipeline.State[status["state"]].stopped()
            status_list.append(status)
    if status and status["state"] == "ERROR":
        raise ValueError("Error in pipeline, please check pipeline-server log messages")
    return status_list

def get_pipeline_status(server_address, instance_id, show_request=False):
    status_url = urljoin(server_address,
                         "/".join(["pipelines",
                                   "status",
                                   str(instance_id)]))
    return get(status_url, show_request)


def _list(server_address, list_name, show_request=False):
    url = urljoin(server_address, list_name)
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
            instance_id = json.loads(launch_response.text)
            return instance_id
    except requests.exceptions.ConnectionError as error:
        raise ConnectionError(SERVER_CONNECTION_FAILURE_MESSAGE) from error
    raise RuntimeError(html_to_text(launch_response.text))

def get(url, show_request=False):
    try:
        if show_request:
            print('GET {}'.format(url))
            sys.exit(0)
        status_response = requests.get(url, timeout=TIMEOUT)
        if status_response.status_code == RESPONSE_SUCCESS:
            return json.loads(status_response.text)
        print("Got unsuccessful status code: {}".format(status_response.status_code))
        print(html_to_text(status_response.text))
    except requests.exceptions.ConnectionError as error:
        raise ConnectionError(SERVER_CONNECTION_FAILURE_MESSAGE) from error
    return None

def delete(url, show_request=False):
    try:
        if show_request:
            print('DELETE {}'.format(url))
            sys.exit(0)
        stop_response = requests.delete(url, timeout=TIMEOUT)
        if stop_response.status_code != RESPONSE_SUCCESS:
            print(html_to_text(stop_response.text))
        return stop_response.status_code
    except requests.exceptions.ConnectionError as error:
        raise ConnectionError(SERVER_CONNECTION_FAILURE_MESSAGE) from error
    return None

def print_fps(status_list):
    sum_of_all_fps = 0
    num_of_pipelines = 0
    for status in status_list:
        if status and 'avg_fps' in status and status['avg_fps'] > 0:
            sum_of_all_fps += status['avg_fps']
            num_of_pipelines += 1
    if num_of_pipelines > 0:
        print('avg_fps: {:.2f}'.format(sum_of_all_fps/num_of_pipelines))

def print_list(item_list):
    for item in item_list:
        print(" - {}/{}".format(item["name"], item["version"]))
