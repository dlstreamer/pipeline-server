# Visualizing Inference Output

There are currently 2 ways to visualize your pipelines from Kubernetes, WebRTC and RTSP. WebRTC is the preferred method to visualize your pipeline to dashboards and websites. RTSP is mostly used for debugging purposes at this moment.

The diagram below shows the methods used to route the output from the pipeline-server pods to external.

![webrtcrtspforwarding](/docs/images/webrtc-port-forwarding.png)

## WebRTC

To get WebRTC to work, you will need a signaling server (STUN or TURN). For demo purposes, we provide a simple signaling server based on WebSocket implementation. 

> **Warning**  This simple signaling server only has a maximum queue of 16 connections at any single point of time.

**Step 1 (Optional if you don't want to use simple signaling server)**: Build signaling server and push to Docker Hub

```bash
cd samples/webrtc/signaling
./build.sh
```

This signalling image will then need to be uploaded to a registry for Kubernetes to pull down this image into the Cluster. In this example, we are using Docker Hub
```bash
docker push webrtc_signaling_server
```

**Step 2**: Update values.yaml with signaling server image and enable WebRTC frame destination

Enable WebRTC frame destination inside values.yaml:

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

**Step 3**: Re-install the cluster

```
cd samples/kubernetes
helm uninstall <release-name>
helm install <release-name> .
```

**Step 4**: Port forward using kubectl. 

You have to port forward 2 things: 
- HTTP from HAProxy at port 80
- WebRTC signalling server at port 8443.

HAProxy (In this case, if release name is dlstreamer, the deployment name is `dlstreamer-haproxy-57c6c98bb6-sxnzb`):
```
kubectl --namespace default port-forward dlstreamer-haproxy-57c6c98bb6-sxnzb 8080:80 --address='0.0.0.0'
```

Expected output:
```
Forwarding from 0.0.0.0:8080 -> 80
<Terminal will hold here>
```

WebRTC Signalling server:

Get the pod name of the signalling server from kubectl
```
kubectl get pods | grep webrtc
```

Expected output:
```
webrtc-server-8b79789d4-h8nd6                         1/1     Running   0              24m
```

Port forward using kubectl for WebRTC signalling server:
```
kubectl --namespace default port-forward webrtc-server-8b79789d4-h8nd6 8443:8443 --address='0.0.0.0'
```

Expected output:
```
Forwarding from 0.0.0.0:8443 -> 8443
<Terminal will hold here>
```

**Step 4**: Run command with webrtc frame destination

**Using pipeline_client.sh**: Change webrtc-peer-id to whatever value you prefer
```bash
./client/pipeline_client.sh start "object_detection/person_vehicle_bike" "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true" --server-address http://localhost:8080  --webrtc-peer-id "pipeline_webrtc1_29442"
```

**Step 5**: View your output via website

You can easily do this by using our webrtc website demo.

```bash
cd samples/webrtc/webserver
docker build -t webrtc-webserver .
docker run -it --rm --user 0 --network host webrtc-webserver
```

**Step 6**: Launch web browser

Please follow the tutorial to enable insecured webrtc under [Configuring Client Browser](/samples/webrtc/README.md#configuring-client-browser)

Launch your preferred browser using this URL, in this example we are using the sample above:

| |                  |
|---------------------------------------------|------------------|
| **destination_peer_id** | This is the peer ID that you set from Step 4 using --webrtc-peer-id. e.g "pipeline_webrtc1_29442" |
| **websocket** | This is the signalling server's address, in this demo, the signalling server will be port forwarded to localhost. |
| **wsport** | This is the signalling server's port, in this demo, the signalling server port is port forwarded to 8443. |

```
http://localhost/?destination_peer_id=pipeline_webrtc1_29442&websocket=localhost&wsport=8443
```
## RTSP

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

> Note: Make sure to reinstall helm

List all the pipeline-server and find the pipeline-server that is running your command:

```bash
kubectl get pods

NAME                                              READY   STATUS             RESTARTS      AGE
dlstreamer-controller-pod-7596f8b658-k4wqv    1/1     Running            1 (83s ago)   87s
dlstreamer-haproxy-77644647c6-wwqtk           1/1     Running            0             63s
dlstreamer-mosquitto-5b5c6b98b6-pql75         1/1     Running            0             87s
dlstreamer-pipeline-server-58859b565b-5c7zp   2/2     Running            1 (82s ago)   87s
dlstreamer-pipeline-server-58859b565b-f6chq   2/2     Running            1 (82s ago)   87s
recycler-for-nfs-exts                             0/1     Completed          0             4d2h
webrtc-server-6d895d9fbd-wwsrn                    0/1     CrashLoopBackOff   3 (44s ago)   87s
```

To discover which pods are running your request, just run `kubectl logs` for each pipeline-server and manually match the UUID.

In this case, `dlstreamer-pipeline-server-58859b565b-5c7zp` is running the server, so we will be port-forwarding 8554.

```bash
kubectl --namespace default port-forward pipelineserver-pipeline-server-58859b565b-5c7zp 8554:8554 --address='0.0.0.0'
```
**Using pipeline_client.sh**: Change `rtsp-path` to a value you prefer
```bash
./client/pipeline_client.sh start "object_detection/person_vehicle_bike" "https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true" --server-address http://localhost:8080  --rtsp-path pserver
```

From here, you can use VLC to view your RTSP output at `rtsp://<host IP>:8554/pserver`.
