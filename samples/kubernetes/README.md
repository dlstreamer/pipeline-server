# Kubernetes Deployment with Load Balancing

| [Definition](#definitions) | [Prerequisites](#prerequisites) | [Building and Deploying Services](#building-and-deploying-services-to-the-cluster) | [Sending Requests](#sending-pipeline-server-requests-to-the-cluster) | [Adding Nodes to Existing Deployment](#adding-nodes-to-an-existing-deployment) | [Examples](#examples) | [Limitations](#limitations) | [Undeploy Services](#undeploy-services) | [Useful Commands](#useful-commands) |

This sample demonstrates how to set up a Kubernetes cluster using MicroK8s, how to deploy Intel(R) Deep Learning Streamer (Intel(R) DL Streamer) Pipeline Server to the cluster, and how to use HAProxy to load balance requests.

![diagram](./kubernetes-diagram.svg)

## Definitions

| Term | Definition |
|---|---|
| Pipeline Server | [Intel(R) DL Streamer Pipeline Server](https://github.com/dlstreamer/pipeline-server) microservice thats runs pipelines. |
| Pipeline Server `CPU` worker | Pipeline Server microservice with Inference runs on `CPU`, check config [here](pipeline-server-worker/deployments/cpu) |
| Pipeline Server `GPU` worker | Pipeline Server microservice with Inference runs on `GPU`, check config [here](pipeline-server-worker/deployments/gpu) |
| HAProxy | [HAProxy](https://www.haproxy.com/) open source load balancer and application delivery controller. |
| MicroK8s | [microk8s](https://microk8s.io/) minimal production Kubernetes distribution. |
| MQTT | [MQTT](https://hub.docker.com/_/eclipse-mosquitto) open source message bus. |
| Node | Physical or virtual machine. |
| Leader | Node hosting the Kubernetes control plane to which worker nodes are added. The leader node can also host pipeline servers and run pipelines. |
| Worker | Nodes hosting pipeline servers. Worker nodes are added to increase the computational resources of the cluster. |
| Pod  | The smallest deployable unit of computing in a Kubernetes cluster, typically a single container. |
| leader-ip | Host IP address of Leader. |

## Prerequisites

| |                  |
|---------------------------------------------|------------------|
| **Docker** | This sample requires Docker for its build, development, and runtime environments. Please install the latest for your platform. [Docker](https://docs.docker.com/install). |
| **bash** | This sample's build and deploy scripts require bash and have been tested on systems using versions greater than or equal to: `GNU bash, version 4.3.48(1)-release (x86_64-pc-linux-gnu)`. Most users shouldn't need to update their version but if you run into issues please install the latest for your platform. |
| **MicroK8s** | This sample requires MicroK8s with DNS setup if system runs under proxy, please follow instructions [here](docs/microk8s.md) to install and Setup Proxy Server DNS  |

## Building and Deploying Services to the Cluster

Use the following command to deploy the Pipeline Server(CPU,GPU), HAProxy and MQTT services to the cluster.

The command
 * Deletes existing Pipeline Server workers.
 * Creates namespace `pipeline-server`, sets it as default and deploys Services in that namespace.
 * Uses the pre built docker image from [intel/dlstreamer-pipeline-server:0.7.2](https://hub.docker.com/r/intel/dlstreamer-pipeline-server). To use a local image instead run `BASE_IMAGE=dlstreamer-pipeline-server-gstreamer:latest ./build_deploy_all.sh`
 * Build and deploys MQTT, Pipeline Server worker and HAProxy. Each node will have one Pipeline Server Worker, if `GPU` available on machine, `GPU` worker will be started, else `CPU` worker.
 * Uses [Kubernetes Node Feature Discovery](https://kubernetes-sigs.github.io/node-feature-discovery/stable/get-started/index.html) and [Intel(R) GPU device plugin for Kubernetes](https://github.com/intel/intel-device-plugins-for-kubernetes/blob/v0.23.0/cmd/gpu_plugin/README.md) to discover, find device resources and enable GPU.
 * Runs script [haproxy/check_for_changes.sh](haproxy/check_for_changes.sh) in background that looks for changes in Pipeline server pods and rebuilds and deploys haproxy.

### Command

```bash
./build_deploy_all.sh
```

### Expected Output

```text
NAME                                  READY   STATUS
mqtt-deployment-64f7b4f5c-89l77       1/1     Running
intel-gpu-plugin-krsch                1/1     Running
pipeline-server-gpu-worker-vknh2      1/1     Running
haproxy-deployment-6c9c989957-9nrkd   1/1     Running
Running process to check for pipeline-server changes in the background
<snip>
```

### Check Status of All Pods

```bash
microk8s kubectl get pods
```

### Expected Output

```text
NAME                                  READY   STATUS
mqtt-deployment-64f7b4f5c-89l77       1/1     Running
intel-gpu-plugin-krsch                1/1     Running
pipeline-server-gpu-worker-vknh2      1/1     Running
haproxy-deployment-6c9c989957-9nrkd   1/1     Running
```

## Sending Pipeline Server Requests to the Cluster

Once pods have been deployed, clients can send pipeline server requests to the cluster via the leader node. The HAProxy service is responsible for load balancing pipeline server requests across the cluster using a `round-robin` algorithm.

When pipeline servers are deployed, they can also be configured to stop taking new requests based on a `MAX_RUNNING_PIPELINES` setting and/or a `TARGET_FPS` setting.

Pipeline servers that reach the configured `MAX_RUNNING_PIPELINES` or have a pipeline instance running with an FPS below the `TARGET_FPS` become unavailable for new requests.

Once all the pipeline servers in the cluster become unavailable, clients receive a `503 Service Unavailable` error from the load balancer. Both `MAX_RUNNING_PIPELINES` and `TARGET_FPS` are set in `pipeline-server-worker/deployments/base/pipeline-server-worker.yaml`.

### Step 1: Start Pipelines on the Cluster

As an example, the following `curl` request starts processing the `homes_00425.mkv` media file with the `object_detection/person_vehicle_bike` pipeline.
This command can be issued multiple times to start multiple concurrent pipelines on the cluster.

> In below command, replace `<leader-ip>` at two places with host ip address of the leader node.

#### Command

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
    }
  }'
```

#### Expected Output

```text
59896b90853511ec838b0242ac110002
```

### Step 2: View Pipeline Results via MQTT

#### Command

```bash
docker run -it  --entrypoint mosquitto_sub  eclipse-mosquitto:1.6 --topic inference-results -p 31020 -h <leader-ip>
```

#### Expected Output

```text
{"objects":[{"detection":{"bounding_box":{"x_max":0.18142173439264297,"x_min":0.0012132003903388977,"y_max":0.5609017014503479,"y_min":0.05551356077194214},"confidence":0.949055016040802,"label":"person","label_id":1},"h":364,"roi_type":"person","w":231,"x":2,"y":40},{"detection":{"bounding_box":{"x_max":0.8925144076347351,"x_min":0.36785489320755005,"y_max":0.9984934628009796,"y_min":0.12739971280097961},"confidence":0.9934169054031372,"label":"vehicle","label_id":2},"h":627,"roi_type":"vehicle","w":672,"x":471,"y":92},{"detection":{"bounding_box":{"x_max":0.6342829465866089,"x_min":0.4171762466430664,"y_max":0.1727554127573967,"y_min":0.006322525441646576},"confidence":0.9811769723892212,"label":"vehicle","label_id":2},"h":120,"roi_type":"vehicle","w":278,"x":534,"y":5},{"detection":{"bounding_box":{"x_max":0.9924979209899902,"x_min":0.8348081111907959,"y_max":0.6326080560684204,"y_min":0.03754556179046631},"confidence":0.51938396692276,"label":"vehicle","label_id":2},"h":428,"roi_type":"vehicle","w":202,"x":1069,"y":27}],"resolution":{"height":720,"width":1280},"source":"https://lvamedia.blob.core.windows.net/public/homes_00425.mkv","timestamp":34233000000}
{"objects":[{"detection":{"bounding_box":{"x_max":0.17737998813390732,"x_min":0.0006547793745994568,"y_max":0.5608647763729095,"y_min":0.05572208762168884},"confidence":0.9445104598999023,"label":"person","label_id":1},"h":364,"roi_type":"person","w":226,"x":1,"y":40},{"detection":{"bounding_box":{"x_max":0.8915983140468597,"x_min":0.3666575849056244,"y_max":0.9976192712783813,"y_min":0.1277613639831543},"confidence":0.9927189350128174,"label":"vehicle","label_id":2},"h":626,"roi_type":"vehicle","w":672,"x":469,"y":92},{"detection":{"bounding_box":{"x_max":0.6342107653617859,"x_min":0.4164556860923767,"y_max":0.17355699837207794,"y_min":0.006252080202102661},"confidence":0.980128824710846,"label":"vehicle","label_id":2},"h":120,"roi_type":"vehicle","w":279,"x":533,"y":5}],"resolution":{"height":720,"width":1280},"source":"https://lvamedia.blob.core.windows.net/public/homes_00425.mkv","timestamp":34267000000}
{"objects":[{"detection":{"bounding_box":{"x_max":0.1800042986869812,"x_min":0.0009236931800842285,"y_max":0.5527437925338745,"y_min":0.04479485750198364},"confidence":0.8942767381668091,"label":"person","label_id":1},"h":366,"roi_type":"person","w":229,"x":1,"y":32},{"detection":{"bounding_box":{"x_max":0.8907946944236755,"x_min":0.3679085373878479,"y_max":0.9973113238811493,"y_min":0.12812647223472595},"confidence":0.9935075044631958,"label":"vehicle","label_id":2},"h":626,"roi_type":"vehicle","w":669,"x":471,"y":92},{"detection":{"bounding_box":{"x_max":0.6346513032913208,"x_min":0.4170849323272705,"y_max":0.17429469525814056,"y_min":0.006016984581947327},"confidence":0.9765880107879639,"label":"vehicle","label_id":2},"h":121,"roi_type":"vehicle","w":278,"x":534,"y":4},{"detection":{"bounding_box":{"x_max":0.9923359751701355,"x_min":0.8340855240821838,"y_max":0.6327562630176544,"y_min":0.03546741604804993},"confidence":0.5069465041160583,"label":"vehicle","label_id":2},"h":430,"roi_type":"vehicle","w":203,"x":1068,"y":26}],"resolution":{"height":720,"width":1280},"source":"https://lvamedia.blob.core.windows.net/public/homes_00425.mkv","timestamp":34300000000}
```


## Adding Nodes to an Existing Deployment

### Step 1: Prepare New Nodes

To add nodes to an existing deployment first follow the steps outlined in [Installing MicroK8s](docs/microk8s.md#installing-microk8s) and [Joining Node to the Cluster](docs/microk8s.md#adding-node-to-the-cluster) for the nodes to be added to the deployment.

### Step 2: Check Status

Pipeline Server should automatically increase the number of deployed CPU/GPU worker pods based on Hardware available on new nodes. HAProxy will be built and deployed automatically for any changes in Pipeline Server pods.
#### Command

```bash
microk8s kubectl get pods
```

#### Expected Output

```text
NAME                                  READY   STATUS
mqtt-deployment-64f7b4f5c-89l77       1/1     Running
intel-gpu-plugin-krsch                1/1     Running
pipeline-server-gpu-worker-vknh2      1/1     Running
pipeline-server-cpu-worker-5gtxg      1/1     Running
haproxy-deployment-6c9c989957-9nrba   1/1     Running
```

## Examples
Find examples [here](docs/examples.md) that demonstrate how we assessed scaling by calculating _stream density_ across a variety of multi-node cluster scenarios.

## Limitations

- Every time a new Intel® DL Streamer Pipeline Server is added or deleted, HAProxy will be restarted automatically to update configuration.
- We cannot yet query full set of pipeline statuses across all Pipeline Server pods. This means `GET <leader-ip>:31000/pipelines/status` may not return complete list.
- When a pipeline runs on a GPU worker, it may take up to 60 seconds to start the pipeline, setting `model-instance-id` with same value limits this issue to the first request as this setting shares resources.

## Undeploy Services

Undeploy Pipeline Server, HAProxy and MQTT services
### Command
```bash
./undeploy_all.sh
```

### Expected Output

```text
<snip>
daemonset.apps "nfd-worker" deleted
service "nfd-master" deleted
deployment.apps "nfd-master" deleted
pod "nfd-worker-z2flv" deleted
pod "nfd-master-75b7c4d897-76f9f" deleted
configmap "kube-root-ca.crt" deleted
daemonset.apps "intel-gpu-plugin" deleted
daemonset.apps "pipeline-server-cpu-worker" deleted
daemonset.apps "pipeline-server-gpu-worker" deleted
service "mqtt-svc" deleted
service "pipeline-server-cpu-service" deleted
service "pipeline-server-gpu-service" deleted
service "haproxy-svc" deleted
deployment.apps "mqtt-deployment" deleted
deployment.apps "haproxy-deployment" deleted
pod "mqtt-deployment-64f7b4f5c-hwbsq" deleted
pod "haproxy-deployment-5d84d7b67-2m9ft" deleted
pod "intel-gpu-plugin-dv8dt" deleted
pod "pipeline-server-gpu-worker-klr2l" deleted
<snip>
Stopped and removed all services
```

## Useful Commands

```bash
# Check running nodes
microk8s kubectl get no

# Check running nodes with detailed information
microk8s kubectl get nodes -o wide

# Check running nodes information in yaml format
microk8s kubectl get nodes -o yaml

# Describe all nodes and details
microk8s kubectl describe nodes

# Describe specific node
microk8s kubectl describe nodes <node-name>

# Get nodes with details of pods running on them
microk8s kubectl get po -A -o wide | awk '{print $6,"\t",$4,"\t",$8,"\t",$2}'

# Deletes pod, after deleting pod, kubernetes may automatically start new on based on replicas
microk8s kubectl delete pod <pod-name>

# Add Service to kubernetes cluster using yaml file
microk8s kubectl apply -f <file.yaml>

# Delete an existing service from cluster
microk8s kubectl delete -f <file.yaml>

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

# Restart Pipeline Server workers
microk8s kubectl rollout restart daemonset pipeline-server-cpu-worker
microk8s kubectl rollout restart daemonset pipeline-server-gpu-worker

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

