# Load Balancing Intel(R) DL Streamer Pipeline Server in Kubernetes

This sample demonstrates deployment of Intel(R) DL Streamer Pipeline Server to Kubernetes using HAProxy load balancer to distribute work across pods in a MicroK8s cluster.

## Definitions

- Pipeline Server : [Intel(R) DL Streamer Pipeline Server](https://github.com/dlstreamer/pipeline-server) microservice thats runs pipelines.
- HAProxy: [HAProxy](https://www.haproxy.com/) open-source load balancer and application delivery controller.
- MicroK8s: [microk8s](https://microk8s.io/) Minimal production Kubernetes distribution.
- MQTT: [MQTT](https://hub.docker.com/_/eclipse-mosquitto) is an open source message bus.
- Node : Physical or virtual machine
- Leader: A Node which acts as controller and used as cluster entrypoint. `leader` can also be used as `worker`, meaning it can perform the function of the worker in addition to the leader. There can only be one leader in a cluster.
- Worker: An additional node attached to leaders cluster to increase efficiency.
- Pod : A pod is a service container that runs jobs.
- leader-ip : Host IP Address of Leader Node.

## Step1: Install Microk8s and dependencies

> If you have multiple nodes, you have to run this step on each node separately.

Starting with your Leader host, prepare your host environment and install prerequisites.
Review the contents of [microk8s/install.sh](microk8s/install.sh) script to understand the changes it will make to your host. This will prepare your host environment, install microk8s and update your user permissions with group membership.

> NOTE: If your host is configured to use a proxy server this should prepare it well. However, you should confirm that this script's updates to `/etc/environment` are not overridden by `/etc/.bash.bashrc`, `~/.bashrc`, `~/.bash_profile`, etc.

Run below command to install microk8s

```bash
cd ./samples/kubernetes
sudo -E ./microk8s/install.sh
```

Upon successful completion it will output the following:

```text
<snip>
Assigning <user name> to microk8s group
```

Your user is now a member of a newly added 'microk8s' group. However, the current terminal session will not be aware of this until you issue this command:

```bash
newgrp microk8s
```

Confirm your user's membership to microk8s in the current terminal session..

```bash
groups | grep microk8s
```

> NOTE: If your host is behind a proxy server, you will need to restart your terminal or run `su - $USER` to ensure environment variables assigned to /etc/environment by ./install.sh are picked up in the current terminal before proceeding to the next step.

Next we need to install add-on components into the cluster. These enable docker registry and dns.

```bash
./microk8s/install_addons.sh
```

Note that this script may take **several minutes** to complete. You should eventually see output in the terminal that includes the status of the add-ons we are enabling:

```text
Started.
Metrics-Server is enabled
DNS is enabled
Ingress is enabled
Metrics-Server is enabled
DNS is enabled
The registry is enabled
```

At this point we need to await the launch of containers that Kubernetes calls "pods" so we will confirm running state before moving on to the next step. It may take few minutes.

Check that installation is successful by confirming Status is `Running` for all pods. These will start in ContainerCreating, Pending, Waiting, but all should eventually reach `Running` status. We have tried to create an resilient script to assure this, but if you encounter difficulty, refer to [application cluster troubleshooting tips](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-pod-replication-controller/).

```bash
microk8s kubectl get pods --all-namespaces
```

```text
NAMESPACE            NAME                                         READY   STATUS    RESTARTS   AGE
kube-system          calico-node-mhvlc                            1/1     Running   0          4m28s
kube-system          metrics-server-8bbfb4bdb-pl6g7               1/1     Running   0          3m1s
kube-system          calico-kube-controllers-f7868dd95-mkjjk      1/1     Running   0          4m30s
kube-system          dashboard-metrics-scraper-78d7698477-pgpkj   1/1     Running   0          86s
kube-system          coredns-7f9c69c78c-8vjr4                     1/1     Running   0          86s
ingress              nginx-ingress-microk8s-controller-rjcpr      1/1     Running   0          86s
kube-system          kubernetes-dashboard-85fd7f45cb-h82gk        1/1     Running   0          86s
kube-system          hostpath-provisioner-5c65fbdb4f-42pdn        1/1     Running   0          86s
container-registry   registry-9b57d9df8-vtmsj                     1/1     Running   0          86s
```

> Troubleshooting Tip: If you see Pending or ContainerCreating after waiting more than a few minutes, you need to modify environment values and restart microk8s. Do this by running `microk8s stop` and `microk8s start`. Then check by running this command again.

### Setup Proxy Server DNS

Apply steps in this section only if your internet traffic flows through a proxy server.

1. Identify host network’s configured DNS servers, run:

    ```bash
    systemd-resolve --status | grep "Current DNS" --after-context=3
    ```

    output

    ```text
    Current DNS Server: 10.22.1.1
                DNS Servers: <ip1>
                              <ip2>
                              <ip3>
    ```

2. Prepare and update DNS configuration.

    Disable DNS

    ```bash
    microk8s disable dns
    ```

    Enable DNS with Configuration

    ```bash
    microk8s enable dns:<ip1>,<ip2>,<ip3>
    ```

    Confirm it’s updated and deployed.

    ```bash
    sh -c "until microk8s.kubectl rollout status deployments/coredns -n kube-system -w; do sleep 5; done"
    ```

    ```text
    deployment "coredns" successfully rolled out
    ```

## Step2: Add a node to cluster

> Note: This step is only required if you have 2 or more nodes, skip otherwise.

For each new node you want to have participate in the cluster, confirm the host has Ubuntu OS and Docker installed.

Issue the following command on your `leader` node. You will need to do this once for each new node you want to add.

```bash
#Run on your primary/leader node
microk8s add-node
```

You should see output as follows, including the IP address of the primary/controller host and unique token for the node you are adding to use during connection to the cluster.

```bash
From the node you wish to join to this cluster, run the following:
microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889

If the node you are adding is not reachable through the default interface you can use one of the following:
 microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
 microk8s join 172.17.0.1:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
```

Run  `join` command shown in the above response on your `worker node`.

```bash
microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
```

You should see output as follows:

```text
Contacting cluster at <host-ip>
Waiting for this node to finish joining the cluster. ..
```

If you encounter an error `Connection failed. Invalid token (500)` your token may have expired or you already used it for another node. To resolve, run the `add-node` command on the leader node to get a new token.

### Confirm Cluster Nodes

To confirm what nodes are running in your cluster, run:

```bash
microk8s kubectl get no
```

You should see output as follows (for example)

```text
NAME         STATUS   ROLES    AGE   VERSION
vcplab003    Ready    <none>   3d    v1.21.5-3+83e2bb7ee39726
vcplab002    Ready    <none>   84s   v1.21.5-3+83e2bb7ee39726
```

## Step3: Build and Deploy

Follow the steps below to build and deploy Pipeline Server, HAProxy and MQTT. The HAProxy service is a single Docker container instance that is responsible for load balancing (e.g., when it receives HTTP requests).
HAProxy is responsible for passing requests to Pipeline servers based on CPU utilization.

> Note: Pipeline Server pod(s) must be up and running before building and deploying HAProxy.

### Pipeline Server Worker

By default replicas in `pipeline-server-worker/pipeline-server.yaml` set to `1` in `line 8`, update this number to number of `nodes` and issue below command.

This command adds host system proxy settings to `pipeline-server-worker/pipeline-server.yaml` and deploys it.

 > The following command uses the pre built docker image from [intel/dlstreamer-pipeline-server:0.7.1](https://hub.docker.com/r/intel/dlstreamer-pipeline-server). To use local image instead run `BASE_IMAGE=dlstreamer-pipeline-server-gstreamer:latest ./pipeline-server-worker/build.sh`

```bash
./pipeline-server-worker/build.sh
./pipeline-server-worker/deploy.sh
```

Wait for Pipeline Server to running.

```bash
microk8s kubectl get pods
```

```text
NAME                                          READY   STATUS
pipeline-server-deployment-7479f5d494-2wkkk   1/1     Running
```

### HAProxy

This will enable REST Requests can be sent through port 31000

```bash
./haproxy/build.sh
./haproxy/deploy.sh
```

Wait for HAProxy to running.

```bash
microk8s kubectl get pods
```

```text
NAME                                          READY   STATUS
pipeline-server-deployment-7479f5d494-2wkkk   1/1     Running
haproxy-deployment-7d79cf66f5-4d92n           1/1     Running
```

### MQTT

This will enable listening to metadata using mosquitto broker.

```bash
./mqtt/deploy.sh
```

Check all Services are up and running, wait until they are set to running.

```bash
microk8s kubectl get pods
```

```text
NAME                                          READY   STATUS
mqtt-deployment-7d85664dc7-f976h              1/1     Running
pipeline-server-deployment-7479f5d494-2wkkk   1/1     Running
haproxy-deployment-7d79cf66f5-4d92n           1/1     Running
```

## Step4: Request Pipeline, listen to metadata

Send the REST request : Using the Leader node IP address and 31000 port to request and 31020 as MQTT port.

> In below command, replace `<leader-ip>` at two places with host ip address.

```bash
 curl <leader-ip>:31000/pipelines/object_detection/person_vehicle_bike -X POST -H \
  'Content-Type: application/json' -d \
  '{
    "source": {
        "uri": "https://lvamedia.blob.core.windows.net/public/homes_00425.mkv",
        "type": "uri"
    },
    "destination": {
        "metadata": {
            "type": "mqtt",
            "host": "<leader-ip>:31020",
            "topic": "inference-results"
        }
    },
    "parameters":{
        "detection-properties": {
            "cpu-throughput-streams": 1,
            "ie-config":"CPU_THREADS_NUM=1,CPU_BIND_THREAD=NO"
        }
    }
  }'
```

### Connect to MQTT broker to view inference results

  ```bash
  docker run -it  --entrypoint mosquitto_sub  eclipse-mosquitto:1.6 --topic inference-results -p 31020 -h <leader-ip>
   ```

## Limitations

- Every time a new Intel® DL Streamer Pipeline Server pod is added or an existing pod restarted, HAProxy needs to be reconfigured and deployed by running below commands

    ```bash
    ./haproxy/build.sh
    ./haproxy/deploy.sh
    ```

- We cannot yet query full set of pipeline statuses across all Pipeline Server pods. Which means `GET <leader-ip>:31000/pipelines/status` may not return complete list.

## Add New worker node to Cluster

1. Run [Step1](#step1-install-microk8s-and-dependencies) and [Step2](#step2-add-a-node-to-cluster) on new node.
2. `On Leader Node` increase replicas and deploy Pipeline Server.

    `On Leader Node` Increase replicas number in `pipeline-server-worker/perline-server.yaml` at `line 8` by 1 and issue below command to add new Pipeline Server pod.

    ```bash
    microk8s kubectl apply -f pipeline-server-worker/pipeline-server.yaml
    ```

    Wait for new Pipeline Server instance to add and set to Running.

    ```bash
    microk8s kubectl get pods | grep 'pipeline-server`
    ```

    ```text
    NAME                                          READY   STATUS
    pipeline-server-deployment-7479f5d494-2wkkk   1/1     Running
    pipeline-server-deployment-7479f5d494-2knop   1/1     Running
    ```

3. Re-configure and deploy HAProxy, this will add new Pipeline Server pod to HAProxy config.

    ```bash
    ./haproxy/build.sh
    ./haproxy/deploy.sh
    ```

    Wait for HAProxy to running.

    ```bash
    microk8s kubectl get pods
    ```

    ```text
    NAME                                          READY   STATUS
    pipeline-server-deployment-7479f5d494-2wkkk   1/1     Running
    pipeline-server-deployment-7479f5d494-2knop   1/1     Running
    haproxy-deployment-7d79cf66f5-4d92n           1/1     Running
    mqtt-deployment-7d85664dc7-f976h              1/1     Running
    ```

4. Cluster is now ready for new requests

## How to undeploy services, delete node or uninstall microk8s?

### Undeploy Pipeline Server, HAProxy and MQTT services

1. Remove Pipeline Server deployment

    ```bash
    microk8s kubectl delete -f pipeline-server-worker/pipeline-server.yaml
    ```

2. Remove HAProxy deployment

    ```bash
    microk8s kubectl delete -f haproxy/haproxy.yaml
    ```

3. Remove MQTT deployment

    ```bash
    microk8s kubectl delete -f mqtt/mqtt.yaml
    ```

### Remove Node

To confirm what nodes are running in your cluster, run:

```bash
microk8s kubectl get no
```

1. Drain the node, run below command in worker node you want to remove

    ```bash
    microk8s kubectl drain <node-name>
    ```

2. Run below command in worker node you want to remove to leave the cluster

    ```bash
    microk8s leave
    ```

3. Run below command on **leader node**

    ```bash
    microk8s remove-node <node-name/ip>
    ```

### Uninstall Microk8s

```bash
./microk8s/uninstall.sh
```

## Debug Commands

```bash
# Check running nodes
microk8s kubectl get no

# Check running nodes with detailed information
microk8s kubectl get nodes -o wide

# Check running nodes information in yaml format
microk8s kubectl get nodes -o yaml

# Decribe all nodes and details
microk8s kubectl describe nodes

# Describe specific node
microk8s kubectl describe nodes <node-name>

# Get nodes with details of pods running on them
microk8s kubectl get po -A -o wide | awk '{print $6,"\t",$4,"\t",$8,"\t",$2}'

# Deletes pod, after deleting pod, kubernetes may automatically start new on based on replicas
microk8s kubectl delete pod name <pod-name>

# Add Service to kubernetes cluster using yaml file
microk8s kubectl apply -f <file.yaml>

# Delete an existing service from cluster
microk8s kubectl delete -f <file.yaml>

# Delete Pipeline Server from cluster
microk8s kubectl delete -f pipeline-server-worker/pipeline-server.yaml

# Delete HAProxy from cluster
microk8s kubectl delete -f haproxy/haproxy.yaml

# Get pods from all namespaces
microk8s kubectl get pods --all-namespaces

# Get pods from default namespace
microk8s kubectl get pods

# Get and follow logs of pod
microk8s kubectl logs -f <pod-name>

# Exec into pod
microk8s kubectl exec -it <pod-name> -- /bin/bash

# Restart a deployment
microk8s kubectl rollout restart deployment <service-name>-deployment

# Restart All Pipeline Server deployments
microk8s kubectl rollout restart deploy pipeline-server-deployment

# Restart HAProxy Service
microk8s kubectl rollout restart deploy haproxy-deployment

# Start microk8s
microk8s start

# Stop microk8s
microk8s stop

# Uninstall microk8s
microk8s reset
sudo snap remove --purge microk8s

# Remove a node from cluster(to be run on a node that needs to be removed)
microk8s leave
```
