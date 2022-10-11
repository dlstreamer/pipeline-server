# Kubernetes Deployment using Helm Charts

| [Architecture](#pipeline-server-kubernetes-architecture-diagram)
| [Installation](#installation)
| [Uninstall](#uninstall-the-cluster)
| [Pipeline Requests](#sending-pipeline-server-requests-to-the-cluster)
| [Persistent Volume](#using-persistent-volume-to-share-models-pipelines-and-extensions)
| [Visualizing Inference Output](#visualizing-inference-output)
| [Values.yaml](#understanding-valuesyaml)
| [Examples](#examples) |

## Pipeline Server Kubernetes Architecture Diagram

Kubernetes Pipeline Server allows users to deploy multiple instances of Pipeline Server while handling network traffic and properly managing workload distribution. It supports processing media analytics on CPU and/or GPU, visual output via RTSP or WebRTC, and utilizes Persistent Volumes for model storage via NFS.

![k8sarchdiagram](/docs/images/k8s-arch-diag.png)

## Installation

> We will be using `helm` to deploy our Kubernetes deployment for pipeline-server. Please install `helm` on your host machine before getting started from here: [Helm Installation](https://helm.sh/docs/intro/install/)

> Current implementation of the Kubernetes cluster deploys a Mosquitto MQTT broke together with the cluster. To receive the MQTT output from the Mosquitto broker, please set the Mosquitto deployment to NodePort.

Step 1: (Optional) Installing Intel GPU Plugin and Node Feature Discovery to enable GPU in your cluster

> Currently we are supporting the use of manual scripts to install Intel GPU Plugin, as the support for Helm is not released yet.

You can set the `number of shared devices` based on the number of GPU pods that you plan to deploy, leaving this blank will default to `1`

```
$ ./samples/kubernetes/dependencies/deploy-gpu-plugin.sh <number of shared devices>
```

Step 2: Build the dependencies from helm

```
$ cd samples/kubernetes
$ helm dep up
```

Step 3: Install pipeline-server into your cluster using default values.yaml. In this example, `dlstreamer` is the release name that is used, you can change this value to any desired value to denote the release name for this deployment.

```
$ cd samples/kubernetes
$ helm install dlstreamer .
```

## Uninstall the Cluster

Step 1: Uninstall the deployment in helm

```sh
$ helm uninstall dlstreamer .
```

Step 2: Uninstall Intel GPU Plugin and NFD

```sh
$ ./samples/kubernetes/dependencies/remove-gpu-plugin.sh
```

## Sending Pipeline Server Requests to the Cluster

Once pods have been deployed, clients can send pipeline server requests to the cluster via HAProxy (Ingress Controller). HAProxy is currently set with `round-robin` algorithm.

### Step 1: Discover the IP Address of the Ingress Controller (HAProxy)

HAProxy is used to mediate the route from the HTTP request to the respective pods. Use `kubectl` to either port-forward port `80` or set HAProxy to NodePort (it is already set to NodePort by default). In this example, I am forwarding port `80` to port `8080`.

```
$ export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=haproxy,app.kubernetes.io/instance=pipelineserver" -o jsonpath="{.items[0].metadata.name}")
$ export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
$ kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
```

### Step 2: Start Pipelines on the Cluster

As an example, the following `curl` request starts processing the `homes_00425.mkv` media file with the `object_detection/person_vehicle_bike` pipeline.
This command can be issued multiple times to start multiple concurrent pipelines on the cluster.

> In below command, replace `<ingress-ip-address>` at places with host ip address of the ingress node (HAProxy).

#### Command

```bash
 curl <ingress-ip-address>:8080/pipelines/object_detection/person_vehicle_bike -X POST -H \
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
59896b90853511ec838b0242ac110002
```

### Step 3 (Optional): Starting GPU Pipelines on the GPU pods in the Cluster

As an example, the following `curl` request starts processing the `person-bicycle-car-detection.mp4` media file with the `object_detection/person_vehicle_bike` pipeline.
This command can be issued multiple times to start multiple concurrent pipelines on the cluster.

> In below command, replace `<ingress-ip-address>` at places with host ip address of the ingress node (HAProxy).

> Important notice, in order to deploy into a GPU pod, you'll need to add the keyword `device` and `GPU` together as the regex detects based on `device.*GPU`. See example below for reference.

#### Command

```bash
curl http://<ingress-ip-address>:8080/pipelines/object_detection/person_vehicle_bike -X POST -H "Content-Type: application/json" -d '{
   "source":{
      "uri":"https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true",
      "type":"uri"
   },
   "destination":{
      "frame":{
         "type":"rtsp",
         "path":"dlstreamer"
      }
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

****

## Using Persistent Volume to Share Models, Pipelines and Extensions

In this example, we used NFS Persistent Volume to store the models, pipelines and extensions.

> **Warning** 
 Due to the constaint of ReadWriteMany or ReadOnlyMany, we recommend using Persistent Volumes that are compatible with ReadWriteMany and ReadOnlyMany. 
Please refer to this [https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes)

Step 1: Deploy your own NFS server (Optional)

> **Note** Skip this steps if you have a PV that is already compatible with ReadOnlyMany or ReadWriteMany

1. Go to your NFS server and install NFS
```
apt update && apt -y upgrade
apt install -y nfs-server
mkdir -p /data/models
mkdir -p /data/extensions
mkdir -p /data/pipelines
cat << EOF >> /etc/exports
/data *(rw,no_subtree_check,no_root_squash)
EOF
systemctl enable --now nfs-server
exportfs -ar
```

That commands will install NFS server and export /data which is accessible by the Kubernetes Cluster and allowing all worker nodes to access it.

2. Prepare Kubernetes worker nodes

Now to connect to the NFS server, every Kubernetes nodes needs an NFS client package to be able to connect to the NFS server. You need to run the following on EVERY Kubernetes WORKERS ONLY. The Control-plane nodes do not require it.

```
apt install -y nfs-common
```

Step 2: Deploy NFS PV (Optional)

> **Note** Skip this steps if you have a PV that is already compatible with ReadOnlyMany or ReadWriteMany

Next, connecting to the NFS by dpeloying PV. In this example, we have provided a simple example of a nfs-pv.yaml to demonstrate this capability.

```
$ cd samples/kubernetes/examples
$ kubectl apply -f nfs-pv.yaml
```

Step 3: Deploy Pipeline Server Kubernetes

Next, to deploy Pipeline Server into Kubernetes using Helm.

First build the dependencies.
```
$ samples/kubernetes/
$ helm dependencies update
```

Next, install pipeline-server into your cluster

```
$ helm install dlstreamer . # Replace dlstreamer with any name you prefer
```

On the first boot, the Persistent Volumes for models, pipelines and extensions will be empty. You will need to populate the models, pipelines and extensions into the respectives directories and then restart pipeline-server on Kubernetes for the changes to take effect.
In my case, I have setup a NFS server linked to /data.

```
1. cd ~/frameworks.ai.dlstreamer.pipeline-server
# /data is my NFS server path that PersistentVolume is linked to
2. sudo cp -r extensions/ /data/extensions 
3. sudo cp -r pipelines/gstreamer /data/pipelines #or ffmpeg if you are using ffmpeg
4. sudo cp -r models/ /data/models
```

Once the data has been copied, restart pipeline-server for pipeline-server to detect the model changes.

```
# Restart pipeline-server to detect the changes on pipeline-server
1. kubectl rollout restart deployments dlstreamer-pipeline-server
```

***

## Visualizing Inference Output

There are currently 2 ways to visualize your pipelines from Kubernetes, WebRTC and RTSP. WebRTC is the preferred method to visualize your pipeline to dashboards and websites. RTSP is mostly used for debugging purposes at this moment.

The diagram below shows the methods used to route the output from the pipeline-server pods to external.

![webrtcrtspforwarding](/docs/images/webrtc-port-forwarding.png)

### WebRTC

To get WebRTC to work, you will need a signaling server (STUN or TURN). For demo purposes, we provide a simple signaling server based on WebSocket implementation. 

> **Warning**  This simple signaling server only has a maximum queue of 16 connection at any single point of time.

**Step 1 (Optional if you don't want to use simple signaling server)**: Build signaling server

```
$ cd frameworks.ai.media-analytics.video-analytics-serving/samples/webrtc/signaling
$ docker build -t webrtc-signaling-server .
```

**Step 2**: Update values.yaml with signaling server image and enable WebRTC frame destination

Enable WebRTC frame destination inside values.yaml:

```
framedestination:
  webrtc:
    enabled: true
```

Update localSignalingServerImageName with your image tag name from Step 1.

```
framedestination:
  webrtc:
    enabled: true
    # Leave localSignalingServerImageName empty if you want to deploy your own signalling server
    localSignalingServerImageName: "webrtc-signaling-server"
```

OR

Leave `localSignalingServerImageName` field empty if you do not wish to use the demo webrtc. This will not deploy the webrtc.

e.g.

```
framedestination:
  webrtc:
    enabled: true
    # Leave localSignalingServerImageName empty if you want to deploy your own signalling server
    localSignalingServerImageName: ""
    url: wss://webrtc.nirbheek.in:8443
```

**Step 3**: Run command with webrtc frame destination

**Using pipeline_client.sh**: Change webrtc-peer-id to whatever value you prefer
```
$ ./client/pipeline_client.sh start "object_detection/person_vehicle_bike" "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true" --webrtc-peer-id "pipeline_webrtc1_29442"
```

**Step 4**: View your output via website

You can easily do this by using our webrtc website demo.

```
$ cd frameworks.ai.media-analytics.video-analytics-serving/samples/webrtc/webserver
$ docker build -t webrtc-webserver .
$ docker run -it --rm --user 0 --network host webrtc-webserver
```

**Step 5**: Launch web browser

Please follow the tutorial to enable insecured webrtc under [Configuring Client Browser](/samples/webrtc/README.md#configuring-client-browser)

You will need to fetch the IP address and port number of your webrtc signaling server if you're using our webrtc demo. To get the port number run `kubectl get svc webrtc-server -o jsonpath='{.spec.ports[0].nodePort}'` and to get the IP address, you need run `kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces | grep webrtc` this will show you which node webrtc-server is running on. 

In my case, my webrtc-server runs on 3054-vcp as seen below.

```
$ kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName --all-namespaces | grep webrtc

webrtc-server-78b6d64f79-4nc2h                   Running     3054-vcp

```

From here, you can get the IP address of your node, in my case 3054-vcp.

```
$ kubectl get nodes -o wide

NAME                 STATUS   ROLES           AGE     VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
3054-vcp             Ready    <none>          5d19h   v1.24.3   10.2.86.31     <none>        Ubuntu 20.04.4 LTS   5.15.0-41-generic   containerd://1.6.6
```

Launch your preferred browser using this URL: http://<Node IP>/?destination_peer_id=<pipeline ID>&websocket=<your websocket URL>&wsport=<port number>

### RTSP

RTSP is visualized by simply port forwarding your RTSP output from your pipeline.

Enable RTSP inside values.yaml:

```
framedestination:
  .
  .
  .
  rtsp:
    enabled: true
```

List all the pipeline-server and find the pipeline-server that is running your command:

```
$ kubectl get pods

NAME                                              READY   STATUS             RESTARTS      AGE
dlstreamer-controller-pod-7596f8b658-k4wqv    1/1     Running            1 (83s ago)   87s
dlstreamer-haproxy-77644647c6-wwqtk           1/1     Running            0             63s
dlstreamer-mosquitto-5b5c6b98b6-pql75         1/1     Running            0             87s
dlstreamer-pipeline-server-58859b565b-5c7zp   2/2     Running            1 (82s ago)   87s
dlstreamer-pipeline-server-58859b565b-f6chq   2/2     Running            1 (82s ago)   87s
recycler-for-nfs-exts                             0/1     Completed          0             4d2h
webrtc-server-6d895d9fbd-wwsrn                    0/1     CrashLoopBackOff   3 (44s ago)   87s
```

To discover which pods are running your request, just run `kubectl get logs` for each pipeline-server and manually match the UUID.

In my case, `dlstreamer-pipeline-server-58859b565b-5c7zp` is running my server, so I'll be port-forwarding 8554.

```
kubectl --namespace default port-forward pipelineserver-pipeline-server-58859b565b-5c7zp 8554:8554 --address='0.0.0.0'
```

From here, you can use VLC to view your RTSP output.

***

## Understanding values.yaml

### Increase number of replicas

values.yaml
```
replicaCount: <number_of_nodes>
```
Upgrade the deployment
```
helm upgrade <release-name> .
```

### Enable control plane for dynamic routing (For multiple pods)

values.yaml
```
controlplane:
  enabled: true
```

### Customizing GPU values

Refer to this doc: [https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md](https://github.com/openvinotoolkit/docker_ci/blob/master/configure_gpu_ubuntu20.md) to understand more about GPU configuration.  

Render group does not have a strict group ID, unlike the video group, please check the group ID for your GPU render and then replace at `renderGroup`

values.yaml
```
gpu:
  # renderGroup depends on your GPU's hardware (e.g. TGL - 109)
  renderGroup: 109
```

### Enable network proxy inside pods

values.yaml
```
network:
  proxy:
    enabled: true
    http: http://<proxy>:<port>
    https: http://<proxy>:<port>
    no_proxy: 10.0.0.0/1
```

### Enable frame destination either WebRTC or RTSP output

values.yaml
```
framedestination:
  webrtc:
    enabled: true
    # Leave localSignalingServerImageName empty if you want to deploy your own signalling server
    localSignalingServerImageName: ""
    # Replace the line below if you want to use your own signalling server (websocket signalling server)
    url: ws://$(WEBRTC_SERVER_SERVICE_HOST):$(WEBRTC_SERVER_SERVICE_PORT)
  rtsp:
    enabled: true
    port: 8554
```

### Customize Persistent Volume

values.yaml
```
persistentVolumeClaim:
  enabled: true
  models:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
  pipelines:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
  exts:
    storageClassName: "<storage-class-name>"
    accessModes: "ReadOnlyMany"
    volumeName: "<volume-name>"
    #Empty string must be explicitly set otherwise default StorageClass will be set
    size: 10Gi
    annotations: {}
```

## Examples

Currently we provide examples under [examples](/samples/kubernetes/examples/) directory.

| Examples | Definition |
|---|---|
| [Securing Kubernetes with HTTPS](/samples/kubernetes/docs/examples.md#securing-k8s.md) | Demo on running Kubernetes with HTTPS |
| [Stream Density example](/samples/kubernetes/docs/examples.md#stream-density-example) | Running various streams with a target of 30fps per stream |
