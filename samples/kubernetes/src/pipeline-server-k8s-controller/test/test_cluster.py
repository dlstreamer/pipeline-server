from cluster import Cluster
from pod import Pod

c = Cluster("default")
p1 = Pod(hostname = "pipeline-server1", \
        ip_address = "10.144.11.113", \
        mac_address = "00:01:00:00:00:00", \
        is_running = True)
c.add_pod(p1)
p2 = Pod(hostname = "pipeline-server2", \
        ip_address = "10.144.11.111", \
        mac_address = "00:00:00:02:00:00", \
        is_running = False)
c.add_pod(p2)
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