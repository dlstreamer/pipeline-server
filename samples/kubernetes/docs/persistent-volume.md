# Share Models, Pipelines and Extensions between Pods

In this example, we used NFS Persistent Volume to store the models, pipelines and extensions.

> **Warning**
  This example is using `persistentVolumeReclaimPolicy: Recycle` which means after EVERY uninstallation or removal of any pods, PVC will attempt to "recycle" or delete all your pipelines, models, extension folder inside the NFS. This is part of the design of the lifecycle of Pods. However, if you do not want this to happen, instead of using PV, you can mount the volumes directly to a Pod without PV.

Step 1: Deploy your own NFS server (Optional)

1. Go to your NFS server and install NFS
```bash
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

```bash
apt install -y nfs-common
```

Step 2: Deploy NFS PV (Optional)

> **Note** Skip this steps if you have a PV that is already compatible with ReadOnlyMany or ReadWriteMany

Next, connecting to the NFS by deploying PV. In this example, we have provided a simple example of a nfs-pv.yaml to demonstrate this capability.

In this sample, you will need to add in your own server and path name inside `samples/kubernetes/examples/nfs-pv.yaml`.

e.g. nfs-pv.yaml
```bash
  metadata:
    name: nfs-pipelines
  .
  .
  .
  nfs:
    server: <your nfs IP address>
    path: <your nfs shared directory that you stored the pipelines in>
  .
  .
  .
  metadata:
    name: nfs-models
  .
  .
  .
  nfs:
    server: <your nfs IP address>
    path: <your nfs shared directory that you stored the models in>
  .
  .
  .
  metadata:
    name: nfs-exts
  .
  .
  .
  nfs:
    server: <your nfs IP address>
    path: <your nfs shared directory that you stored the extensions in>
```


```bash
cd samples/kubernetes/examples
kubectl apply -f nfs-pv.yaml
```

Step 3: Enable PersistentVolume in values.yaml

Update values.yaml to enable PersistentVolume:

```yaml
persistentVolumeClaim:
  enabled: true
```

> ***NOTE*** To simplify this example, we have set the `volumeName` for each respective directory inside the values.yaml based on the nfs-pv.yaml. Change this value if you are deploying your own PersistentVolume.

Step 4: Deploy Pipeline Server Kubernetes

Next, to deploy Pipeline Server into Kubernetes using Helm.

First build the dependencies.
```bash
samples/kubernetes/
helm dependencies update
```

Next, install pipeline-server into your cluster

```bash
helm install dlstreamer . # Replace dlstreamer with any name you prefer
```

On the first boot, the Persistent Volumes for models, pipelines and extensions will be empty. You will need to populate the models, pipelines and extensions into the respectives directories and then restart pipeline-server on Kubernetes for the changes to take effect.
In this case, we have setup a NFS server linked to /data.

```bash
cd ~/frameworks.ai.dlstreamer.pipeline-server
# In this sample, /data is the NFS server path that PersistentVolume is linked to
sudo cp -r extensions/ /data/extensions 
sudo cp -r pipelines/gstreamer/* /data/pipelines #or ffmpeg if you are using ffmpeg
sudo cp -r models/ /data/models
```

Once the data has been copied, restart pipeline-server for pipeline-server to detect the model changes.

You can get the `deployment` names using `kubectl get deployment`

```bash
kubectl get deployment
```

```text
NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
dlstreamer-controller-pod        1/1     1            1           4m40s
dlstreamer-haproxy               1/1     1            1           4m40s
dlstreamer-mosquitto             1/1     1            1           4m40s
dlstreamer-pipeline-server-cpu   1/1     1            1           4m40s
dlstreamer-pipeline-server-gpu   1/1     1            1           4m40s
```

From there, you can restart the pipeline-server deploying for both cpu and gpu
> **Warning**
  If you using port-forwarding as shown in the first step, after restarting, you'll need to port forward again.

```bash
# Restart pipeline-server to detect the changes on pipeline-server
kubectl rollout restart deployments dlstreamer-pipeline-server-cpu
kubectl rollout restart deployments dlstreamer-pipeline-server-gpu
```

Step 5: Remove NFS from the Kubernetes Cluster

You can remove the NFS using the usual `kubectl` command:

```
kubectl delete -f nfs-pv.yaml
```