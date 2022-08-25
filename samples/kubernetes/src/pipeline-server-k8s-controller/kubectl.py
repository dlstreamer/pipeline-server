#!/usr/bin/env python3
'''
* Copyright (C) 2019-2020 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
import datetime

from kubernetes import config, dynamic, client
from kubernetes.dynamic import exceptions
from kubernetes.client import api_client

class KubeCtl:
    def __init__(self, k8s_namespace = "default"):
        try:
            self.k8s_namespace = k8s_namespace
            self.dynamic_client = dynamic.DynamicClient(\
                                                        api_client.ApiClient(
                                                        configuration=config.load_incluster_config()))
            self.configmap_api = self.dynamic_client.resources.get(api_version="v1", kind="ConfigMap")
            self.deployment_api = self.dynamic_client.resources.get(api_version="v1", kind="Deployment")
            self.client_corev1api = client.CoreV1Api()
        except config.ConfigException as config_exception:
            raise Exception("Could not configure kubernetes python client. \
                            Please check your service account and ensure that \
                            it has been configured properly.") from config_exception

    def patch_cm_data(self, configmap_object_name: str, config_name: str, config_data: str) -> None:
        """
        Replace a config-map based on a configuration file.

        :param configmap_object_name: name of ConfigMap object
        :param config_name: configuration file to patch
        :param config_data: configuration content to patch
        :return: None

        api.patch \
        name=settings namespace=default data='{"example.conf": "# example file"}'
        """
        configmap_manifest = {
            "data": {
                config_name: config_data,
            },
        }

        self.configmap_api.patch(name=configmap_object_name, \
                                                      namespace=self.k8s_namespace, \
                                                      body=configmap_manifest)
        print("ConfigMap patched")

    def create_cm(self, configmap_object_name: str, config_name: str, config_data: str) -> None:
        """
        Create a config-map based on a configuration file.

        :param configmap_object_name: name of ConfigMap object
        :param config_name: configuration file
        :param config_data: configuration content
        :return: None

        api.create \
        name=settings namespace=default data='{"example.conf": "# example file"}'
        """
        configmap_manifest = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": configmap_object_name,
            },
            "data": {
                config_name: config_data,
            },
        }
        try:
            self.configmap_api.create(body=configmap_manifest, namespace=self.k8s_namespace)
        except exceptions.ConflictError:
            print("ConfigMap already exist")
        else:
            print("ConfigMap created")

    def rollout_deployment(self, deployment_object_name: str) -> None:
        """
        Restart deployment based on deployment_object_name.

        :param deployment_object_name: name of ConfigMap object
        :return: None

        api.patch \
        name=settings namespace=default data='{"example.conf": "# example file"}'
        """
        now = datetime.datetime.utcnow()
        now = str(now.isoformat("T") + "Z")
        deployment_manifest = {
            'spec': {
                'template':{
                    'metadata': {
                        'annotations': {
                            'kubectl.kubernetes.io/restartedAt': now
                        }
                    }
                }
            }
        }
        try:
            self.deployment_api.patch(name=deployment_object_name, \
                                                            namespace=self.k8s_namespace, \
                                                            body=deployment_manifest)
        except Exception:
            print("Failed to rollout Deployment {}".format(deployment_object_name))
        else:
            print("Deployment {} rollout".format(deployment_object_name))


    def get_pods(self, name: str) -> dict:
        """
        Get all metadata on a pod based on name and namespace.

        :param name: name of Pod object
        :return: dict of pods
        """
        pods = {}
        try:
            ret = self.client_corev1api.list_namespaced_pod(self.k8s_namespace)
            for pod in ret.items:
                if pod.metadata.namespace == self.k8s_namespace and name in pod.metadata.name:
                    if not (pod.metadata.deletion_timestamp is not None and pod.status.phase == 'Running'):
                        pods[pod.metadata.name] = pod.status.pod_ip
            return pods
        except Exception as except_list:
            raise Exception("Failed to get list of pods for {}".format(name)) from except_list

    def count_pods(self, name: str) -> int:
        """
        Returns the number of pods based on the name.

        :param name: name of Pod object
        :return: number of pods
        """
        try:
            pods = self.get_pods(name)
            return len(pods)
        except Exception as except_count:
            raise Exception("Failed to count number of pods {}".format(name)) from except_count

    def get_pods_names(self, name: str) -> list:
        """
        Returns the names of pods based on params.

        :param name: name of Pod object
        :return: list of pods names
        """
        try:
            pods = self.get_pods(name)
            return list(pods.keys())
        except Exception as except_pods:
            raise Exception("Failed to get pods names {}".format(name)) from except_pods

    def get_pod_ip_from_name(self, name: str) -> str:
        """
        Returns the IP address of pods based on params.

        :param name: name of Pod object
        :return: str of IP address
        """
        try:
            pods = self.get_pods(name)
            return pods[name]
        except Exception as except_pod_name:
            raise Exception("Failed to get IP address from pod names: {}".format(name)) from except_pod_name
