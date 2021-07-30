#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
import time
from threading import Thread
WATCHER_POLL_TIME = 0.01

class ResultsWatcher:
    def __init__(self, filename, sleep_time=WATCHER_POLL_TIME):
        self.filename = filename
        self.sleep_time = sleep_time
        self.watcher_thread = None
        self.trigger_stop = False
        self.error_message = None

    def watch(self):
        self.watcher_thread = Thread(target=self.watch_method)
        self.trigger_stop = False
        self.watcher_thread.start()

    def stop(self):
        self.trigger_stop = True
        self.watcher_thread.join()
        if self.error_message:
            raise OSError(self.error_message)

    def watch_method(self):
        try:
            file = open(self.filename, 'r')
            while not self.trigger_stop:
                where = file.tell()
                line = file.readline()
                if not line:
                    time.sleep(self.sleep_time)
                    file.seek(where)
                else:
                    try:
                        ResultsWatcher.print_results(json.loads(line))
                    except ValueError:
                        pass
        except OSError:
            self.error_message = "Unable to read from destination metadata file {}".format(self.filename)

    # Print Functions
    @classmethod
    def print_results(cls, results):
        """Output as JSON formatted data"""
        if "timestamp" in results:
            print("Timestamp {}".format(results["timestamp"]))
        for index, detected_object in enumerate(results.get("objects", [])):
            meta = {}
            results_output = []
            for key in detected_object:
                if key == "detection":
                    confidence = detected_object[key]["confidence"]
                    label = detected_object[key]["label"]
                    x_min = detected_object[key]["bounding_box"]["x_min"]
                    y_min = detected_object[key]["bounding_box"]["y_min"]
                    x_max = detected_object[key]["bounding_box"]["x_max"]
                    y_max = detected_object[key]["bounding_box"]["y_max"]
                    results_output.append(label)
                    results_output.append("({:.2f})".format(confidence))
                    results_output.append("[{:.2f}, {:.2f}, {:.2f}, {:.2f}]".format(x_min,
                                                                                    y_min,
                                                                                    x_max,
                                                                                    y_max))
                elif key == "id":
                    meta[key] = detected_object[key]
                elif isinstance(detected_object[key], dict) and "label" in detected_object[key]:
                    meta[key] = detected_object[key]["label"]
                elif key == "tensors":
                    for tensor in detected_object[key]:
                        if "name" in tensor and tensor["name"] == "action":
                            confidence = tensor["confidence"]
                            label = tensor["label"]
                            results_output.append(label)
                            results_output.append("({:.2f})".format(confidence))
            if meta:
                results_output.append(str(meta))
            print("- {}".format(" ".join(results_output)))
            
        for event in results.get("events", []):
            event_str = "Event: "
            for key in event:
                event_str += "{}: {}, ".format(key, event[key])
            print(event_str.rstrip(', '))              
            
