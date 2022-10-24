#!/usr/bin/env python3
'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from pod import Pod
from xpu import Xpu

class Cluster:
    def __init__(self, namespace = "default"):
        self.namespace = namespace
        self.pods = []

    def get_pod_by_hostname(self, hostname) -> Pod:
        """
        Returns pod based on hostname.

        :return: Pod
        """
        for pod in self.pods:
            if pod.hostname == hostname:
                return pod
        return None

    def get_pod_by_ip_address(self, ip_address) -> Pod:
        """
        Returns pod based on IP Address.

        :return: Pod
        """
        for pod in self.pods:
            if pod.ip_address == ip_address:
                return pod
        return None

    def get_pod_by_mac_address(self, mac_address) -> Pod:
        """
        Returns pod based on MAC Address.

        :return: Pod
        """
        for pod in self.pods:
            if pod.mac_address == mac_address:
                return pod
        return None

    def get_hostnames(self) -> list:
        """
        Returns list of hostname.

        :return: list
        """
        tmp = []
        for pod in self.pods:
            tmp.append(pod.hostname)
        return tmp

    def get_ip_addresses(self, xpu_type = None) -> list:
        """
        Returns list of IP Address.

        :param xpu_type: Xpu enum datatype
        :return: list
        """
        tmp = []
        for pod in self.pods:
            if pod.xpu_type == Xpu.CPU and xpu_type == Xpu.CPU:
                tmp.append(pod.ip_address)
            elif pod.xpu_type == Xpu.GPU and xpu_type == Xpu.GPU:
                tmp.append(pod.ip_address)
            elif xpu_type is None:
                tmp.append(pod.ip_address)
        return tmp

    def get_mac_addresses(self, xpu_type = None) -> list:
        """
        Returns list of MAC Address.

        :param xpu_type: Xpu enum datatype
        :return: list
        """
        tmp = []
        for pod in self.pods:
            if pod.xpu_type == Xpu.CPU and xpu_type == Xpu.CPU:
                tmp.append(pod.mac_address)
            elif pod.xpu_type == Xpu.GPU and xpu_type == Xpu.GPU:
                tmp.append(pod.mac_address)
            elif xpu_type is None:
                tmp.append(pod.mac_address)
        return tmp

    def add_pod(self, pod: Pod) -> None:
        """
        Adds Pod datatype into Cluster, doesn't add if there's an existing Pod in the Cluster.

        :param pod: Pod datatype
        :return: None

        Pod(hostname = "pipeline-server1", ip_address = "10.144.11.111", \
            mac_address = "00:00:00:00:00:00", is_running = True)
        """
        if pod not in self.pods:
            self.pods.append(pod)

    def remove_pod(self, pod: Pod) -> None:
        """
        Remove Pod datatype from Cluster, doesn't rmeove if Pod doesn't exist in the Cluster.

        :param pod: Pod datatype
        :return: None

        Pod(hostname = "pipeline-server1", ip_address = "10.144.11.111", \
            mac_address = "00:00:00:00:00:00", is_running = True)
        """
        if pod in self.pods:
            self.pods.remove(pod)

    def __len__(self):
        return len(self.pods)
