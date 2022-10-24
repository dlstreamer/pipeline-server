#!/usr/bin/env python3
'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from kubectl import KubeCtl

k = KubeCtl("default")
print(k.count_pods("pipeline-server"))
print(k.get_pods_names("pipeline-server"))
print(k.get_pod_ip_from_name("pipelineserver-pipeline-server-ff894467b-ph2d9"))
k.create_cm("server-maps-haproxy", "servers.map", "{}")
k.rollout_deployment("pipelineserver-haproxy")
