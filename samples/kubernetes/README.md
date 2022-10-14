# Kubernetes Deployment using Helm Charts

| [Architecture](#pipeline-server-kubernetes-architecture-diagram)
| [Prerequisites](#prerequisites)
| [Getting Started](#getting-started)
| [Pipeline Requests](#sending-pipeline-server-requests-to-the-cluster)
| [Uninstall](#uninstall-the-cluster)
| [Learn more](#learn-more) |

## Pipeline Server Kubernetes Architecture Diagram

Kubernetes Pipeline Server allows users to deploy multiple instances of Pipeline Server while handling network traffic and properly managing workload distribution. It supports processing media analytics on CPU and/or GPU, visual output via RTSP or WebRTC, and utilizes Persistent Volumes for model storage via NFS.

![k8sarchdiagram](/docs/images/k8s-arch-diag.png)

## Prerequisites

| |                  |
|---------------------------------------------|------------------|
| **Kubernetes** | To run this deployment, an access to a Kubernetes cluster is required. Instructions for installing Kubernetes cluster can be found [here](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/). |
| **Helm** | This deployment uses Helm as the package manager to ship Pipeline Server. Instructions to install Helm can be found [here](https://helm.sh/docs/intro/install/) |

## Getting Started

Step 1: (Optional) Installing Intel GPU Plugin and Node Feature Discovery (NFD) to enable GPU in your cluster

> **Note**: Currently we are supporting the use of manual scripts to install Intel GPU Plugin, as the support for Helm is not released yet.

You can set the `number of shared devices` this determines the number of containers that can share the same GPU device, leaving this blank will default to `2`.

```bash
./samples/kubernetes/dependencies/deploy-gpu-plugin.sh <number of shared devices>
```

Step 2: Build the dependencies from helm

```bash
cd samples/kubernetes
helm dep up
```

Step 3: Install pipeline-server into your cluster using default values.yaml. In this example, `dlstreamer` is the release name that is used, you can change this value to any desired value to denote the release name for this deployment. We will store our release name inside `RELEASE_NAME` variable as we will need this in the later steps.

```bash
RELEASE_NAME=dlstreamer

cd samples/kubernetes
helm install $RELEASE_NAME .
```

## Sending Pipeline Server Requests to the Cluster

Once pods have been deployed, clients can send pipeline server requests to the cluster via HAProxy (Ingress Controller). HAProxy is currently set with `round-robin` algorithm.

### Step 1: Discover the IP Address of the Ingress Controller (HAProxy)

HAProxy is used to mediate the route from the HTTP request to the respective pods. Use `kubectl` to either port-forward port `80` or set HAProxy to NodePort (it is already set to NodePort by default). In this example, we will be forwarding port `80` to port `8080`.

```bash
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=haproxy,app.kubernetes.io/instance=$RELEASE_NAME" -o jsonpath="{.items[0].metadata.name}")
export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```

### Step 2: Start Pipelines on the Cluster

As an example, the following `curl` request starts processing the `homes_00425.mkv` media file with the `object_detection/person_vehicle_bike` pipeline.
This command can be issued multiple times to start multiple concurrent pipelines on the cluster. Open a new terminal and run this commands.

> In this example, we are using `localhost` because we have port forwarded it to localhost in Step 1.

#### Command

```bash
 curl http://localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
  'Content-Type: application/json' -d \
  '{
    "source": {
        "uri": "https://lvamedia.blob.core.windows.net/public/homes_00425.mkv",
        "type": "uri"
    }
  }'
```

#### Expected Output

```text
b85bcc1c4ae711ed8c79aa43cc2acc79
```

To check the pipeline you can use `/pipelines/status` which queries the status of all running pipelines in the cluster.

#### Command

```bash
 curl http://localhost:8080/pipelines/status
```

#### Expected Output

```json
[
    {
        "avg_fps": 27.59946173763987,
        "elapsed_time": 1.4492945671081543,
        "id": "b85bcc1c4ae711ed8c79aa43cc2acc79",
        "message": "",
        "start_time": 1665659462.319232,
        "state": "RUNNING"
    }
]
```

### Step 3 (Optional): Starting GPU Pipelines on the GPU pods in the Cluster

In this example, we will be specifying the device that we would like the pipeline to start in. Notice in the example given below, `"detection-device": "GPU",` has been added to the parameters's request in order to deploy into a GPU pod. See example below for reference. If `detection-device` is not set, the pipeline will be started in a pod that is selected based on `round-robin` algorithm. 

> In this example, we are using `localhost` because we have port forwarded it to localhost in Step 1.

#### Command

```bash
curl http://localhost:8080/pipelines/object_detection/person_vehicle_bike -X POST -H "Content-Type: application/json" -d '{
   "source":{
      "uri":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type":"uri"
   },
   "parameters": {
      "detection-device": "GPU",
      "detection-model-instance-id": "detect_object_detection_person_vehicle_bike_GPU"
   }
}'
```

#### Expected Output

```text
59896b90853511ec838b0242ac110002
```

## Uninstall the Cluster

Step 1: Uninstall the deployment in helm

```bash
helm uninstall dlstreamer
```

Step 2: Uninstall Intel GPU Plugin and NFD

```bash
./samples/kubernetes/dependencies/remove-gpu-plugin.sh
```

***

## Learn more

There are various examples and documentation under [examples](/samples/kubernetes/examples/) and [docs](/samples/kubernetes/docs/) to help understand how Kubernetes can work with Pipeline Server.

| Examples & Tutorials | Definition |
|---|---|
| [Sharing Models, Pipelines & Extensions between Pods](./docs/persistent-volume.md | Tutorial of using Persistent Volume to share models, pipelines and extensions between Pods
| [Visualizing Inference Output](./docs/visualizing-inference.md) | Tutorial to view the inference output from pipelines
| [Values.yaml](./docs/understanding-values-yaml.md) | Documentation to explain about values.yaml
| [Securing Kubernetes with HTTPS](./docs/securing-k8s.md) | Demo on running Kubernetes with HTTPS |
| [Stream Density example](./docs/stream-density.md) | Running various streams using Pipeline Client |