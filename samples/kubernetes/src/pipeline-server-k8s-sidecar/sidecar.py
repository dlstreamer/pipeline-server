#!/usr/bin/env python3
'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import uuid
import socket
import os

import paho.mqtt.client as mqtt
from paho.mqtt import publish

class Sidecar:
    def __init__(self, k8s_namespace, k8s_releasename, mac_address):
        self.k8s_namespace = k8s_namespace
        self.k8s_releasename = k8s_releasename
        self.hostname = socket.gethostname()
        self.macaddr = mac_address
        self.topic = "MAC"
        self.mqtt_broker = os.getenv(self.k8s_releasename.upper() + "_MOSQUITTO_SERVICE_HOST")
        self.mqtt_port = int(os.getenv(self.k8s_releasename.upper() + "_MOSQUITTO_SERVICE_PORT"))

    def publish_mqtt(self, payload):
        publish.single(self.topic, payload=payload ,qos=2, hostname=self.mqtt_broker, port=self.mqtt_port)
        print("Just published " + self.hostname + ';' + self.macaddr + " to topic " + self.topic)

    def on_message(self, _unused_client, _unused_userdata, message):
        """
        MQTT on_message

        :param _unused_client: unused
        :param _unused_userdata: unused
        :param message: object containing the message received from MQTT

        This function retrieves any messages that contains 'request' in the message.
        If `request` keyword exist, then publish our own MAC Address and Hostname to the topic.
        """

        dmessage = str(message.payload.decode("utf-8"))
        pod_state = dmessage.split(';', maxsplit=1)[0]
        if pod_state == "request":
            payload = "add;{};{}".format(self.hostname, self.macaddr)
            self.publish_mqtt(payload)
        print(f"received message: {dmessage}")

if __name__ == "__main__":
    mac_address = str(uuid.uuid1()).rsplit('-', maxsplit=1)[-1]
    client = mqtt.Client("Sidecar{}".format(mac_address))
    releasename = os.getenv("MY_RELEASE_NAME")
    sidecar = Sidecar(os.getenv("MY_NAMESPACE"), releasename, mac_address)
    mqtt_broker = os.getenv(releasename.upper() + "_MOSQUITTO_SERVICE_HOST")
    mqtt_port = int(os.getenv(releasename.upper() + "_MOSQUITTO_SERVICE_PORT"))
    topic = "MAC"
    print ('services running')
    client.connect(mqtt_broker, mqtt_port)
    client.subscribe(topic)
    client.on_message=sidecar.on_message
    print ('running mqtt...')
    client.loop_forever()
