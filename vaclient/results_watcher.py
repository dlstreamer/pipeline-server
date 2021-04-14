#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
import time
import sys
from threading import Thread
WATCHER_POLL_TIME = 0.01

class ResultsWatcher:
    def __init__(self, filename, sleep_time=WATCHER_POLL_TIME):
        self.filename = filename
        self.sleep_time = sleep_time
        self.watcher_thread = None
        self.trigger_stop = False

    def watch(self):
        self.watcher_thread = Thread(target=self.watch_method)
        self.trigger_stop = False
        self.watcher_thread.start()

    def stop(self):
        self.trigger_stop = True
        self.watcher_thread.join()

    def watch_method(self):
        file = open(self.filename, 'r')
        try:
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
        except KeyboardInterrupt:
            sys.exit(0)

    # Print Functions
    @classmethod
    def print_results(cls, obj):
        """Output as JSON formatted data"""
        print("Timestamp {}".format(obj["timestamp"]))
        for objects in obj["objects"]:
            meta = {}
            for key in objects:
                if key == "detection":
                    confidence = objects[key]["confidence"]
                    label = objects[key]["label"]
                    x_min = objects[key]["bounding_box"]["x_min"]
                    y_min = objects[key]["bounding_box"]["y_min"]
                    x_max = objects[key]["bounding_box"]["x_max"]
                    y_max = objects[key]["bounding_box"]["y_max"]
                elif key == "id":
                    meta[key] = objects[key]
                elif isinstance(objects[key], dict) and "label" in objects[key]:
                    meta[key] = objects[key]["label"]
            print("- {} ({:.2f}) [{:.2f}, {:.2f}, {:.2f}, {:.2f}] {}".format(label,
                                                                             confidence,
                                                                             x_min,
                                                                             y_min,
                                                                             x_max,
                                                                             y_max,
                                                                             str(meta)))
