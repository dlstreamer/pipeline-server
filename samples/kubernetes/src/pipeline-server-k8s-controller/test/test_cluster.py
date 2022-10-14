#!/usr/bin/env python3
'''
* Copyright (C) 2022 Intel Corporation.
*
* SPDX-License-Identifier: BSD-3-Clause
'''
from cluster import Cluster
from pod import Pod
from xpu import Xpu

c = Cluster("default")
p1 = Pod(hostname = "pipeline-server1", \
        ip_address = "10.144.11.113", \
        mac_address = "00:01:00:00:00:00", \
        is_running = True, xpu_type = Xpu.CPU)
c.add_pod(p1)

p2 = Pod(hostname = "pipeline-server2", \
        ip_address = "10.144.11.111", \
        mac_address = "00:00:00:02:00:00", \
        is_running = False, xpu_type = Xpu.GPU)
c.add_pod(p2)

# Failing test case
p3 = Pod(hostname = "pipeline-server3", \
        ip_address = "10.144.11.121", \
        mac_address = "04:00:00:00:00:00", \
        is_running = False)
c.add_pod(p3)

print(c.pods)
c.remove_pod(p2)
print(c.pods)
c.remove_pod(p2)
print(c.pods)
try:
    print(c.get_pod_by_hostname("pipeline-server1"))
    print(c.get_pod_by_ip_address("10.144.11.111"))
    print(c.get_pod_by_mac_address("04:00:00:00:00:00"))
except Exception as e:
    print("{}".format(e))
