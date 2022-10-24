#!/usr/bin/python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import json
import time
import os
import socket
from threading import Thread, Event
from abc import ABC, abstractmethod
from kafka import KafkaConsumer, TopicPartition
import paho.mqtt.client as mqtt


WATCHER_POLL_TIME = 0.01

class ResultsWatcher(ABC):

    def __init__(self):
        self._error_message = "Results Watcher OK"
        self._watching = False
        self._display = True

    def __del__(self):
        if self._watching:
            self.stop()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def watching(self):
        return self._watching

    def error_message(self):
        return self._error_message

    @staticmethod
    def print_results(results):
        object_output = []
        for detected_object in results.get("objects", []):
            object_output.append(ResultsWatcher._process_detections(detected_object))
        event_output = []
        for event in results.get("events", []):
            current_event = []
            for key in event:
                current_event.append("{}: {}".format(key, event[key]))
            if current_event:
                event_output.append("Event: {}".format(", ".join(current_event)))
        if "timestamp" in results and (object_output or event_output):
            print("Timestamp {}".format(results["timestamp"]), flush=True)
        if object_output:
            print("{}".format("\n".join(object_output)), flush=True)
        if event_output:
            print("{}".format("\n".join(event_output)), flush=True)

    @staticmethod
    def _process_detections(detected_object):
        meta = {}
        current_object = []
        for key in detected_object:
            if key == "detection":
                confidence = detected_object[key]["confidence"]
                label = detected_object[key]["label"]
                bbox = detected_object[key]["bounding_box"]
                current_object.append(label)
                current_object.append("({:.2f})".format(confidence))
                current_object.append("[{:.2f}, {:.2f}, {:.2f}, {:.2f}]"
                    .format(bbox["x_min"],
                            bbox["y_min"],
                            bbox["x_max"],
                            bbox["y_max"]))
            elif key == "id":
                meta[key] = detected_object[key]
            elif isinstance(detected_object[key], dict) and "label" in detected_object[key]:
                meta[key] = detected_object[key]["label"]
            elif key == "tensors":
                for tensor in detected_object[key]:
                    if "name" in tensor and tensor["name"] == "action":
                        confidence = tensor["confidence"]
                        label = tensor["label"]
                        current_object.append(label)
                        current_object.append("({:.2f})".format(confidence))
        if meta:
            current_object.append(str(meta))
        if current_object:
            return "- {}".format(" ".join(current_object))
        return ""


class FileWatcher(ResultsWatcher):

    def __init__(self, destination, sleep_time=WATCHER_POLL_TIME):
        super().__init__()
        self.filename = destination["path"]
        self.sleep_time = sleep_time
        self.watcher_thread = None
        self.trigger_stop = False
        self._started_event = Event()
        self.watcher_thread = Thread(target=self._watch_method)

    def start(self):
        self.watcher_thread.start()
        self._started_event.wait()

    def stop(self):
        if self._watching:
            self.trigger_stop = True
            self.watcher_thread.join()

    def _watch_method(self):
        try:
            with open(self.filename, 'r') as file:
                self._watching = True
                self._started_event.set()
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
            self._watching = False
        except OSError:
            self.error_message = "Unable to read from file {}".format(self.filename)
            self._started_event.set()


class MqttWatcher(ResultsWatcher):
    def __init__(self, destination):
        super().__init__()
        self._client = mqtt.Client("Intel(R) DL Streamer Results Watcher", userdata=destination)
        if os.environ["MQTT_CLUSTER_BROKER"]:
            mqtt_host = os.environ["MQTT_CLUSTER_BROKER"]
            broker_address = mqtt_host.split(':')
        else:
            broker_address = destination["host"].split(':')
        self._host = broker_address[0]
        if len(broker_address) == 2:
            self._port = int(broker_address[1])
        else:
            self._port = 1883
        self._topic = destination["topic"]
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._started_event = Event()

    def on_connect(self, client, _unused_user_data, _unused_flags, return_code):
        if return_code == 0:
            client.subscribe(self._topic)
            self._watching = True
            self._started_event.set()
        else:
            print("Error {} connecting to broker {}:{}".format(return_code, self._host, self._port))

    def on_message(self, _unused_client, _unused_user_data, msg):
        result = json.loads(msg.payload)
        ResultsWatcher.print_results(result)

    def start(self):
        self._client.connect(self._host, self._port)
        self._client.loop_start()
        self._started_event.wait()

    def stop(self):
        self._client.unsubscribe(self._topic)
        self._client.loop_stop()
        self._watching = False

class KafkaWatcher(ResultsWatcher):
    def __init__(self, destination):
        super().__init__()
        self.watcher_thread = None
        self._consumer = None
        self._watching = False
        self.trigger_stop = False
        try:
            self._client_id = socket.gethostname()
            self._timeout_ms = 1000
            self._topic = destination["topic"]
            self._bootstrap_servers = [destination["host"]]
            self._consumer=KafkaConsumer(
                bootstrap_servers=self._bootstrap_servers,
                client_id=self._client_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                max_poll_interval_ms=self._timeout_ms,
                consumer_timeout_ms=self._timeout_ms,
                api_version=(0,10))
        except Exception as exception:
            self.error_message = exception
            print("KafkaWatcher error - {}".format(exception))

    def start(self):
        try:
            if self._consumer:
                self._watching = True
                self.trigger_stop = False
                self.watcher_thread = Thread(target=self._watch_method)
                self.watcher_thread.start()
        except Exception as exception:
            self.error_message = exception

    def stop(self):
        if self._watching:
            self.trigger_stop = True
            self.watcher_thread.join()
        if self._consumer:
            self._consumer.close()
            self._consumer = None

    def _watch_method(self):
        if self._consumer:
            partitions=self._consumer.partitions_for_topic(self._topic)
            if not partitions:
                raise Exception("Topic {} not exist".format(self._topic))
            self._consumer.assign([TopicPartition(self._topic,p) for p in partitions])
            self._consumer.seek_to_beginning()
            while self._consumer and not self.trigger_stop:
                partitions=self._consumer.poll(self._timeout_ms)
                if partitions:
                    for partition in partitions:
                        for message in partitions[partition]:
                            ResultsWatcher.print_results(json.loads(message.value.decode('utf-8')))
            self._watching = False


def create(request):
    try:
        destination = request['destination']['metadata']
        if "type" in destination:
            watcher_type = destination["type"]
            if watcher_type == "file":
                return FileWatcher(destination)
            if watcher_type == "kafka":
                return KafkaWatcher(destination)
            if watcher_type == "mqtt":
                return MqttWatcher(destination)
            print("Metadata type {} not supported".format(watcher_type))
    except Exception as exception:
        print("Cannot create watcher: {}".format(exception))
    return None
