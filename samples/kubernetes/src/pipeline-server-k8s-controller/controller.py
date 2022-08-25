#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''

import os
import threading
import time

import asyncio
import paho.mqtt.client as mqtt

from cluster import Cluster
from pod import Pod
from kubectl import KubeCtl
from controller_server import RunServer
from cluster_watch import ClusterWatch

class Controller:
    def __init__(self, k8s_namespace, k8s_releasename):
        self.haproxy = ''
        self.servermap = ''
        self.k8s_namespace = k8s_namespace
        self.k8s_releasename = k8s_releasename
        self.kubectl = KubeCtl(k8s_namespace)
        #Workaround
        self.kubectl.create_cm("server-maps-haproxy", "servers.map", "{}")
        self.cluster = Cluster(self.k8s_namespace)

    def update_ingress_controller_config(self, haproxy, servermap):
        self.kubectl.patch_cm_data(self.k8s_releasename + "-haproxy", "haproxy.cfg", haproxy)
        #Workaround
        self.kubectl.patch_cm_data("server-maps-haproxy", "servers.map", servermap)
        self.kubectl.rollout_deployment(self.k8s_releasename + "-haproxy")

    def update_config_map(self):
        _server_map_file_macaddrs = self.cluster.get_mac_addresses()
        _server_map_file_ipaddrs = self.cluster.get_ip_addresses()
        self.servermap = ''

        with open("haproxy-template.cfg", "r") as file_haproxy:
            self.haproxy = file_haproxy.read()
        self.haproxy = self.haproxy.replace("this line is updated by script\n", "", 1)
        for index, server_map_file_macaddr in enumerate(_server_map_file_macaddrs):
            self.haproxy = self.haproxy + \
                           "    server {}_server {}:8080 check weight 100 agent-check        agent-addr {} \
                            agent-port 3333 agent-inter 1s  agent-send ping \n" \
                            .format(server_map_file_macaddr, _server_map_file_ipaddrs[index], \
                            _server_map_file_ipaddrs[index])

        self.haproxy += "\n\n"

        for index, server_map_file_macaddr in enumerate(_server_map_file_macaddrs):
            self.haproxy = self.haproxy + "backend pipeline-server{}\n".format(index)
            self.haproxy = self.haproxy + "  server {}_server {}:8080 check\n"\
                                          .format(server_map_file_macaddr, _server_map_file_ipaddrs[index])

        counter = 0
        for controller_pod_name in self.kubectl.get_pods_names("controller-pod"):
            controller_api_ipaddr = self.kubectl.get_pod_ip_from_name(controller_pod_name)
            # Append the Controller Pod as a backend
            self.haproxy = self.haproxy + "backend controller_api{}\n".format(counter)
            self.haproxy = self.haproxy + "  server controller_server{} {}:8080 check\n"\
                                          .format(counter, controller_api_ipaddr)
            counter += 1

        for index, server_map_file_macaddr in enumerate(_server_map_file_macaddrs):
            self.servermap += server_map_file_macaddr + "     pipeline-server{}\n".format(index)

        self.update_ingress_controller_config(self.haproxy, self.servermap)

    def on_message(self, _unused_client, _unused_userdata, message):
        # Only call update_database if the number of pod counts == number of dmessage received
        dmessage = str(message.payload.decode("utf-8"))
        pod_state = dmessage.split(';', maxsplit=1)[0]
        if pod_state == "add":
            pod_state, hostname, mac_address = dmessage.split(';', 2)
            try:
                ip_address = self.kubectl.get_pod_ip_from_name(hostname)
                if ip_address:
                    pod = Pod(hostname = hostname, ip_address = ip_address, \
                              mac_address = mac_address, is_running = True)
                    if pod not in self.cluster.pods:
                        self.cluster.add_pod(pod)
                        # Only update config map once pod count is same as pod in cluster
                        if self.kubectl.count_pods("pipeline-server") == len(self.cluster):
                            self.update_config_map()
            except Exception:
                print("Can't get IP Address, most likely the {} pod has been removed.".format(hostname))
        elif pod_state == "remove":
            hostnames = dmessage.split(';')[1:]
            for hostname in hostnames:
                # manually check which pod to remove based on hostname and IP address
                pod_by_hostname = self.cluster.get_pod_by_hostname(hostname)
                if pod_by_hostname:
                    print ("Pod with hostname {} is removed".format(pod_by_hostname))
                    self.cluster.remove_pod(pod_by_hostname)
                else:
                    print("Pod with {} doesn't exist or has already been removed".format(pod_by_hostname))
            if self.kubectl.count_pods("pipeline-server") == len(self.cluster):
                self.update_config_map()
        else:
            print("Unknown pod_state: {}".format(pod_state))
        print("received message: {}".format(dmessage))

def run_cluster_watch():
    print ('running cluster watch...')
    cw.watch()

def run_tornado():
    print ('running tornado...')
    asyncio.set_event_loop(asyncio.new_event_loop())
    server.run_server()

def run_mqtt():
    print ('running mqtt...')
    releasename = os.getenv("MY_RELEASE_NAME")
    controller = Controller(os.getenv("MY_NAMESPACE"), releasename)
    mqtt_broker = os.getenv(releasename.upper() + "_MOSQUITTO_SERVICE_HOST")
    mqtt_port = int(os.getenv(releasename.upper() + "_MOSQUITTO_SERVICE_PORT"))
    topic = "MAC"
    client.connect(mqtt_broker, mqtt_port)
    client.subscribe(topic)
    client.on_message=controller.on_message
    client.loop_start()

if __name__ == "__main__":
    server = RunServer()
    client = mqtt.Client("Controller")
    cw = ClusterWatch()
    for target in (run_mqtt, run_tornado, run_cluster_watch):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
    print ('services running, press ctrl+c to stop')
    while True:
        time.sleep(1)
