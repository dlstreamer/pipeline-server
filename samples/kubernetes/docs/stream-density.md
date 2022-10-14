# Stream Density Example

These examples will show the following using Pipeline Client:

- Running a single stream on a single node. This indicates a stream density of at least 1.
- Running four streams on a single node. This indicates a stream density of 4.
- Adding a second node to cluster and running eight streams on both nodes. This indicates a stream density of 8 and that we are scaling effectively with each node added to the cluster.
- Adding a third node to cluster and running 30 streams across 3 nodes. This indicates we are utilizing all available resources across the cluster's nodes to run our workloads.

The examples require [pipeline_client](/client/README.md) so the container `dlstreamer-pipeline-server-gstreamer` must be built as per [these instructions](/README.md#building-the-microservice).

## Single Node with MQTT

### Port forward MQTT and HTTP endpoint

As Mosquitto MQTT Broker resides in the Cluster, you'll need to port forward the MQTT Broker to your host machine in another terminal. Similarly do the same for the HTTP endpoint in another terminal.

1. Open a new terminal and get the Mosquitto MQTT Broker's deployment name:
```
kubectl get pods | grep -i mosquitto
```

Expected output:
```
dlstreamer-mosquitto-5b5c6b98b6-dhtp6         1/1     Running     0             26m
```

2. Port forward using kubectl. (In this case, the deployment name is `dlstreamer-mosquitto-5b5c6b98b6-dhtp6`)

```
kubectl --namespace default port-forward dlstreamer-mosquitto-5b5c6b98b6-dhtp6 1883:1883 --address='0.0.0.0'
```

Expected output:
```
Forwarding from 0.0.0.0:1883 -> 1883
<Terminal will hold here>
```

3. Open another terminal and get the HAProxy's deployment name:
```
kubectl get pods | grep haproxy
```

Expected output:
```
dlstreamer-haproxy-57c6c98bb6-sxnzb               1/1     Running   0             11h
```

4. Port forward using kubectl. (In this case, the deployment name is `dlstreamer-haproxy-57c6c98bb6-sxnzb`)

```
kubectl --namespace default port-forward dlstreamer-haproxy-57c6c98bb6-sxnzb 8080:80 --address='0.0.0.0'
```

Expected output:
```
Forwarding from 0.0.0.0:8080 -> 80
<Terminal will hold here>
```

Start stream as follows

```bash
# Get MQTT Broker deployment name
MQTTBROKER=$(kubectl get deployment | grep -i mosquitto | cut -f1 -d' ')

./client/pipeline_client.sh run object_detection/person_vehicle_bike \
  https://lvamedia.blob.core.windows.net/public/homes_00425.mkv \
  --server-address http://localhost:8080 \
  --destination type mqtt --destination host $MQTTBROKER:1883 --destination topic person-vehicle-bike --mqtt-cluster-broker localhost:1883
```

Output should be like this (with different instance id and timestamps)

```text
Starting pipeline object_detection/person_vehicle_bike, instance = e6846cce838311ecaf588a37d8d13e4f
Pipeline running - instance_id = e6846cce838311ecaf588a37d8d13e4f
Timestamp 5300000000
- person (0.73) [0.03, 0.21, 0.22, 0.87]
- vehicle (0.97) [0.42, 0.01, 0.63, 0.17]
- vehicle (0.83) [0.39, 0.12, 0.89, 0.99]
- vehicle (0.52) [0.82, 0.05, 0.99, 0.64]
Timestamp 5333000000
- person (0.97) [0.05, 0.20, 0.23, 0.85]
- vehicle (0.97) [0.42, 0.01, 0.63, 0.17]
- vehicle (0.84) [0.39, 0.12, 0.89, 0.99]
- vehicle (0.54) [0.83, 0.05, 0.99, 0.64]
```

Now stop stream using CTRL+C, pipeline will be in `ABORTED` state after.

```text
^C
Stopping Pipeline...
Pipeline stopped
- vehicle (0.99) [0.39, 0.13, 0.89, 1.00]
- vehicle (0.99) [0.42, 0.00, 0.63, 0.17]
avg_fps: 123.33
Done
```

## Single Node with Four Streams

For four streams, we won't use MQTT but will measure fps by querying the `/pipelines/status` endpoint (i.e. can we attain a stream density of 4). Note the use of [model-instance-id](/docs/defining_pipelines.md#model-persistance-in-openvino-gstreamer-elements) so pipelines can share resources.

```bash
./client/pipeline_client.sh run object_detection/person_vehicle_bike \
  https://lvamedia.blob.core.windows.net/public/homes_00425.mkv \
  --server-address http://localhost:8080 \
  --parameter detection-model-instance-id person-vehicle-bike \
  --number-of-streams 4
```

```text
Starting pipeline 1
Starting pipeline object_detection/person_vehicle_bike, instance = 73dd289eb06211ec9dc75ef1db0c4cdf
Pipeline 1 running - instance_id = 73dd289eb06211ec9dc75ef1db0c4cdf
Starting pipeline 2
Starting pipeline object_detection/person_vehicle_bike, instance = 794fcd9ab06211ec9dc75ef1db0c4cdf
Pipeline 2 running - instance_id = 794fcd9ab06211ec9dc75ef1db0c4cdf
Starting pipeline 3
Starting pipeline object_detection/person_vehicle_bike, instance = 7faaf5cab06211ec9dc75ef1db0c4cdf
Pipeline 3 running - instance_id = 7faaf5cab06211ec9dc75ef1db0c4cdf
Starting pipeline 4
Starting pipeline object_detection/person_vehicle_bike, instance = 8651bb16b06211ec9dc75ef1db0c4cdf
Pipeline 4 running - instance_id = 8651bb16b06211ec9dc75ef1db0c4cdf
4 pipelines running.
Pipeline status @ 39s
- instance=73dd289eb06211ec9dc75ef1db0c4cdf, state=RUNNING, 53fps
- instance=794fcd9ab06211ec9dc75ef1db0c4cdf, state=RUNNING, 37fps
- instance=7faaf5cab06211ec9dc75ef1db0c4cdf, state=RUNNING, 36fps
- instance=8651bb16b06211ec9dc75ef1db0c4cdf, state=RUNNING, 30fps
```

Results show that stream density of four achieved.

Use CTRL+C to stop streams, pipeline will be in `ABORTED` state after.

```text
<snip>
Pipeline status @ 76s
- instance=73dd289eb06211ec9dc75ef1db0c4cdf, state=ABORTED, 41fps
- instance=794fcd9ab06211ec9dc75ef1db0c4cdf, state=ABORTED, 31fps
- instance=7faaf5cab06211ec9dc75ef1db0c4cdf, state=ABORTED, 30fps
- instance=8651bb16b06211ec9dc75ef1db0c4cdf, state=ABORTED, 30fps
avg_fps: 33
Done
```

## Eight Streams on Two Nodes

We'll add a second node to see if we can get a stream density of eight as per [Increase number of replicas](./understanding-values-yaml.md#increase-number-of-replicas) by increasing either `cpuReplicaCount` or `gpuReplicaCount`.

Now we run eight streams and monitor fps using the same request as before. This time the work should be shared across the two nodes.

```bash
./client/pipeline_client.sh run object_detection/person_vehicle_bike \
  https://lvamedia.blob.core.windows.net/public/homes_00425.mkv \
  --server-address http://localhost:8080 \
  --parameter detection-model-instance-id person-vehicle-bike \
  --number-of-streams 8
```

```text
<snip>
Starting pipeline 1
Starting pipeline object_detection/person_vehicle_bike, instance = 9268a11cac9311ec9d92aa618d1feb05
Pipeline 1 running - instance_id = 9268a11cac9311ec9d92aa618d1feb05
<snip>
Starting pipeline 8
Starting pipeline object_detection/person_vehicle_bike, instance = 96ad090cac9311ec984ec2ba86c884b6
Pipeline 8 running - instance_id = 96ad090cac9311ec984ec2ba86c884b6
8 pipelines running.
Pipeline status @ 18s
- instance=9268a11cac9311ec9d92aa618d1feb05, state=RUNNING, 35fps
- instance=9302aca8ac9311ec984ec2ba86c884b6, state=RUNNING, 37fps
- instance=93a1b230ac9311ec9d92aa618d1feb05, state=RUNNING, 33fps
- instance=943af9b8ac9311ec984ec2ba86c884b6, state=RUNNING, 34fps
- instance=94d9f50eac9311ec9d92aa618d1feb05, state=RUNNING, 32fps
- instance=9573da48ac9311ec984ec2ba86c884b6, state=RUNNING, 32fps
- instance=96138fa2ac9311ec9d92aa618d1feb05, state=RUNNING, 31fps
- instance=96ad090cac9311ec984ec2ba86c884b6, state=RUNNING, 32fps
```

See all the streams have state=RUNNING if so, a stream density of 8 has been achieved.

Use CTRL+C to stop streams, pipeline will be in `ABORTED` state after.

```text
<snip>
Pipeline status @ 82s
- instance=9268a11cac9311ec9d92aa618d1feb05, state=ABORTED, 35fps
- instance=9302aca8ac9311ec984ec2ba86c884b6, state=ABORTED, 35fps
- instance=93a1b230ac9311ec9d92aa618d1feb05, state=ABORTED, 32fps
- instance=943af9b8ac9311ec984ec2ba86c884b6, state=ABORTED, 33fps
- instance=94d9f50eac9311ec9d92aa618d1feb05, state=ABORTED, 32fps
- instance=9573da48ac9311ec984ec2ba86c884b6, state=ABORTED, 32fps
- instance=96138fa2ac9311ec9d92aa618d1feb05, state=ABORTED, 31fps
- instance=96ad090cac9311ec984ec2ba86c884b6, state=ABORTED, 32fps
avg_fps: 32.75
Done
```

## 30 Streams on Three Nodes

We'll add a third node to see if we can get a stream density of 30 as per [Increase number of replicas](./understanding-values-yaml.md#increase-number-of-replicas) by increasing either `cpuReplicaCount` or `gpuReplicaCount`.

Now we run 30 streams and monitor fps using the same request as before. This time the work should be shared across the three nodes.

```bash
./client/pipeline_client.sh run object_detection/person_vehicle_bike \
  https://lvamedia.blob.core.windows.net/public/homes_00425.mkv \
  --server-address http://localhost:8080 \
  --parameter detection-model-instance-id person-vehicle-bike \
  --number-of-streams 30
```

```text
<snip>
Starting pipeline 1
Starting pipeline object_detection/person_vehicle_bike, instance = 83eedaf6b05411eca1ccd2862a904e11
Pipeline 1 running - instance_id = 83eedaf6b05411eca1ccd2862a904e11
Starting pipeline 2
Starting pipeline object_detection/person_vehicle_bike, instance = 84da6610b05411ec95675e5f5863e7f7
Pipeline 2 running - instance_id = 84da6610b05411ec95675e5f5863e7f7
<snip>
Starting pipeline 29
Starting pipeline object_detection/person_vehicle_bike, instance = bb43dddab05411eca1ccd2862a904e11
Pipeline 29 running - instance_id = bb43dddab05411eca1ccd2862a904e11
Starting pipeline 30
Starting pipeline object_detection/person_vehicle_bike, instance = bbe191bab05411eca1ccd2862a904e11
Pipeline 30 running - instance_id = bbe191bab05411eca1ccd2862a904e11
30 pipelines running.
Pipeline status @ 14s
- instance=83eedaf6b05411eca1ccd2862a904e11, state=COMPLETED, 475fps
- instance=84da6610b05411ec95675e5f5863e7f7, state=RUNNING, 51fps
- instance=87445302b05411ec9defc23594411cd1, state=RUNNING, 55fps
- instance=89fecb4ab05411eca1ccd2862a904e11, state=COMPLETED, 477fps
- instance=8a9c9870b05411ec95675e5f5863e7f7, state=RUNNING, 38fps
- instance=90a9cb84b05411ec9defc23594411cd1, state=RUNNING, 37fps
- instance=9758a734b05411eca1ccd2862a904e11, state=COMPLETED, 555fps
- instance=97f66096b05411ec95675e5f5863e7f7, state=RUNNING, 31fps
- instance=9db662ecb05411ec9defc23594411cd1, state=RUNNING, 31fps
- instance=a41838d6b05411eca1ccd2862a904e11, state=COMPLETED, 549fps
- instance=a4b5b4e4b05411ec95675e5f5863e7f7, state=RUNNING, 29fps
- instance=aac2ed5cb05411ec9defc23594411cd1, state=RUNNING, 28fps
- instance=b1729d64b05411eca1ccd2862a904e11, state=RUNNING, 90fps
- instance=b210451eb05411eca1ccd2862a904e11, state=RUNNING, 70fps
- instance=b2ad1452b05411eca1ccd2862a904e11, state=RUNNING, 60fps
- instance=b34a2c88b05411eca1ccd2862a904e11, state=RUNNING, 54fps
- instance=b3e754d6b05411eca1ccd2862a904e11, state=RUNNING, 49fps
- instance=b4842090b05411eca1ccd2862a904e11, state=RUNNING, 45fps
- instance=b5212c96b05411eca1ccd2862a904e11, state=RUNNING, 42fps
- instance=b5be3676b05411eca1ccd2862a904e11, state=RUNNING, 40fps
- instance=b65b602cb05411eca1ccd2862a904e11, state=RUNNING, 38fps
- instance=b6f87196b05411eca1ccd2862a904e11, state=RUNNING, 37fps
- instance=b7956d66b05411eca1ccd2862a904e11, state=RUNNING, 35fps
- instance=b832b314b05411eca1ccd2862a904e11, state=RUNNING, 34fps
- instance=b8cf8608b05411eca1ccd2862a904e11, state=RUNNING, 33fps
- instance=b96c52e4b05411eca1ccd2862a904e11, state=RUNNING, 32fps
- instance=ba09b476b05411eca1ccd2862a904e11, state=RUNNING, 32fps
- instance=baa6cfd6b05411eca1ccd2862a904e11, state=RUNNING, 31fps
- instance=bb43dddab05411eca1ccd2862a904e11, state=RUNNING, 30fps
- instance=bbe191bab05411eca1ccd2862a904e11, state=RUNNING, 30fps
```

See all 30 streams have state=RUNNING if so, a stream density of 30 has been achieved.

Use CTRL+C to stop streams, pipeline will be in `ABORTED` state after.

```text
<snip>
Pipeline status @ 14s
- instance=83eedaf6b05411eca1ccd2862a904e11, state=COMPLETED, 475fps
- instance=84da6610b05411ec95675e5f5863e7f7, state=COMPLETED, 42fps
- instance=87445302b05411ec9defc23594411cd1, state=ABORTED, 40fps
- instance=89fecb4ab05411eca1ccd2862a904e11, state=COMPLETED, 477fps
- instance=8a9c9870b05411ec95675e5f5863e7f7, state=ABORTED, 35fps
- instance=90a9cb84b05411ec9defc23594411cd1, state=ABORTED, 34fps
- instance=9758a734b05411eca1ccd2862a904e11, state=COMPLETED, 555fps
- instance=97f66096b05411ec95675e5f5863e7f7, state=ABORTED, 31fps
- instance=9db662ecb05411ec9defc23594411cd1, state=ABORTED, 30fps
- instance=a41838d6b05411eca1ccd2862a904e11, state=COMPLETED, 549fps
- instance=a4b5b4e4b05411ec95675e5f5863e7f7, state=ABORTED, 31fps
- instance=aac2ed5cb05411ec9defc23594411cd1, state=ABORTED, 29fps
- instance=b1729d64b05411eca1ccd2862a904e11, state=ABORTED, 43fps
- instance=b210451eb05411eca1ccd2862a904e11, state=ABORTED, 39fps
- instance=b2ad1452b05411eca1ccd2862a904e11, state=ABORTED, 36fps
- instance=b34a2c88b05411eca1ccd2862a904e11, state=ABORTED, 35fps
- instance=b3e754d6b05411eca1ccd2862a904e11, state=ABORTED, 34fps
- instance=b4842090b05411eca1ccd2862a904e11, state=ABORTED, 33fps
- instance=b5212c96b05411eca1ccd2862a904e11, state=ABORTED, 32fps
- instance=b5be3676b05411eca1ccd2862a904e11, state=ABORTED, 32fps
- instance=b65b602cb05411eca1ccd2862a904e11, state=ABORTED, 31fps
- instance=b6f87196b05411eca1ccd2862a904e11, state=ABORTED, 31fps
- instance=b7956d66b05411eca1ccd2862a904e11, state=ABORTED, 31fps
- instance=b832b314b05411eca1ccd2862a904e11, state=ABORTED, 31fps
- instance=b8cf8608b05411eca1ccd2862a904e11, state=ABORTED, 31fps
- instance=b96c52e4b05411eca1ccd2862a904e11, state=ABORTED, 30fps
- instance=ba09b476b05411eca1ccd2862a904e11, state=ABORTED, 30fps
- instance=baa6cfd6b05411eca1ccd2862a904e11, state=ABORTED, 30fps
- instance=bb43dddab05411eca1ccd2862a904e11, state=ABORTED, 30fps
- instance=bbe191bab05411eca1ccd2862a904e11, state=ABORTED, 30fps
avg_fps: 97.26
Done
```
