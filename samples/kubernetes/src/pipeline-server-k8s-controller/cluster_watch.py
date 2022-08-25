#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import logging
from paho.mqtt import publish
from kubernetes import client, config, watch
from urllib3.exceptions import ProtocolError

class ClusterWatch():
    def __init__(self, log_level = "INFO"):
        self.releasename = os.getenv("MY_RELEASE_NAME")
        self.mqtt_broker = os.getenv(self.releasename.upper() + "_MOSQUITTO_SERVICE_HOST")
        self.mqtt_port = int(os.getenv(self.releasename.upper() + "_MOSQUITTO_SERVICE_PORT"))
        self.topic = "MAC"
        self.flag = False
        self.logger = logging.getLogger("clusterwatch")
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        self.logger.setLevel(log_level)
        payload = "request;"
        publish.single(self.topic, payload=payload ,qos=2,\
                        hostname=self.mqtt_broker, port=self.mqtt_port)
        config.load_incluster_config()
        self.api_instance = client.CoreV1Api()

    def publish_mqtt(self, payload):
        publish.single(self.topic, payload=payload ,qos=2, hostname=self.mqtt_broker, port=self.mqtt_port)

    def watch(self) -> None:
        """
        Watches the cluster for changes in number of pipeline-server pods.
        Setting self.flag = True will stop this watch.

        :return: None
        """
        while self.flag is False:
            watch_cluster = watch.Watch()
            try:
                for event in watch_cluster.stream(self.api_instance.list_namespaced_pod, namespace="default"):
                    if event['object'].status.container_statuses is not None and \
                       "pipeline-server" in event['object'].metadata.name and \
                        event['object'].status.container_statuses[-1].state.running is not None:
                        if event['object'].metadata.deletion_timestamp is not None:
                            self.logger.info("Event DELETED")
                            payload = "remove"
                            payload = "{};{}".format(payload, event['object'].metadata.name)
                            self.logger.info("Payload is {}".format(payload))
                            self.publish_mqtt(payload)
                            self.logger.info("Just published {} to topic {}".format(payload, self.topic))
                        elif event['object'].status.container_statuses[-1].state.running:
                            self.logger.info("Event ADDED")
                            payload = "request;"
                            self.publish_mqtt(payload)
                        self.logger.info("Event: {} {} {}".format(event['type'],event['object'].kind, \
                                                            event['object'].metadata.name))
            except ProtocolError:
                self.logger.error("watchPodEvents ProtocolError, continuing..")

if __name__ == "__main__":
    cw = ClusterWatch()
    cw.watch()
