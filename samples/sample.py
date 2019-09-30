#!/usr/bin/python3
'''
* Copyright (C) 2019 Intel Corporation.
* 
* SPDX-License-Identifier: BSD-3-Clause
'''

import requests
import urllib.parse
import json
import time
import os
from optparse import OptionParser
import statistics

video_analytics_serving = "http://localhost:8080/pipelines/"
timeout = 30
sleep_for_status = 0.5

request_template = {
    "source": {
        "uri": "file:///home/video-analytics/samples/pinwheel.ts",
        "type": "uri"
    },
    "destination": {
        "path": "/home/video-analytics/samples/results.txt",
        "type": "file",
        "format":"stream"
    }
}

def get_options():
    parser = OptionParser()
    parser.add_option("--pipeline", action="store", dest="pipeline",
                      type="string", default='object_detection')
    parser.add_option("--source", action="store", dest="source",
                      type="string", default='file:///home/video-analytics/samples/pinwheel.ts')
    parser.add_option("--destination", action="store", dest="destination",
                      type="string", default='/home/video-analytics/samples/results.txt')
    parser.add_option("--repeat", action="store", dest="repeat",
                      type="int", default=1)
    parser.add_option("--quiet", action="store_false", dest="verbose", default=True)

    return parser.parse_args()

def print_json(object):
    print(json.dumps(object,
                     sort_keys=True,
                     indent=4,
                     separators=[',',': ']))
    
def read_detection_results(destination,verbose=True):
    if (verbose): # pylint: disable=superfluous-parens
        object_lines=[]
        with open(destination) as file:
            for line in file:
                try:
                    if line=="{\n":
                        object_lines.append(line)
                        line=None
                        
                    if object_lines:
                        if line:
                            object_lines.append(line)
                        if line=='}\n':
                            line="".join(object_lines)
                            object_lines=[]
                        else:
                            line=None

                    if line:
                        print("Detection Result: \n")
                        print_json(json.loads(line))
                except Exception as error:
                    print(error)
                
def wait_for_pipeline(instance_id,
                      pipeline="object_detection",
                      version="1",
                      verbose=True):
    status = {"state":"RUNNING"}
    while((status["state"]=="RUNNING") or (status["state"]==None) or (status["state"]=="QUEUED")):
        status=get_status(instance_id,pipeline,version)
        if status==None:
            return None
        if (verbose): # pylint: disable=superfluous-parens
            print("Pipeline Status:\n")
            print_json(status)
        time.sleep(sleep_for_status)
    return status

def get_status(instance_id,
               pipeline="object_detection",
               version="1"):
    
    status_url = urllib.parse.urljoin(video_analytics_serving,
                                      "/".join([pipeline,
                                                version,
                                                str(instance_id),"status"]))

    try:
        r = requests.get(status_url,timeout=timeout)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            None
    except requests.exceptions.RequestException as e:
        return None
    
def start_pipeline(stream_uri,
                   pipeline,
                   destination,
                   version="1",
                   tags=None,
                   parameters=None,
                   verbose=True):

    request = request_template
    request["source"]["uri"] = stream_uri

    try:
        os.remove(os.path.abspath(destination))
    except OSError:
        pass

    request["destination"]["path"] = os.path.abspath(destination)
    if tags and len(tags) > 0:
        request["tags"] = tags
    if parameters and len(parameters) > 0:
        request["parameters"] = parameters
    pipeline_url = urllib.parse.urljoin(video_analytics_serving,
                                        pipeline+"/"+version)

    if (verbose): # pylint: disable=superfluous-parens
        print("Starting Pipeline: %s" % (pipeline_url))

    try:
        r = requests.post(pipeline_url, json=request, timeout=timeout)
        if r.status_code == 200:
            instance_id = int(r.text)
            return instance_id
    except requests.exceptions.RequestException as e:
        return None
    
def print_stats(status,key='avg_fps'):
    values = [x[key] for x in status if x and key in x and 'state' in x and x['state']=="COMPLETED"]

    if len(values):
        stats = {"value":key,
                 "Average":statistics.mean(values),
                 "Variance":statistics.variance(values),
                 "Max":max(values),
                 "Min":min(values),
                 "Count":len(status)
        }
        print_json(stats)
    else:
        print("No results")
    
if __name__ == "__main__":

    try:
        options, args = get_options()
    except Exception as error:
        print(error)
        logger.error("Getopt Error!")
        exit(1)
    status=[]
    for i in range(options.repeat):
        instance_id=start_pipeline(options.source,options.pipeline,options.destination,verbose=options.verbose)
        status.append(wait_for_pipeline(instance_id,options.pipeline,verbose=options.verbose))
        read_detection_results(options.destination,verbose=options.verbose)
        
    if len(status)>1:
        print_stats(status)
        print_stats(status,key="elapsed_time")
