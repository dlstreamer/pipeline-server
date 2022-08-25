# MicroK8s

| [Installing Microk8s](#installing-microk8s) | [Adding Node](#adding-node-to-the-cluster) | [Removing Node](#removing-node-from-cluster) | [Uninstalling Microk8s](#uninstalling-microk8s)

The following steps, installation and deployment scripts have been tested on Ubuntu 20.04. Other operating systems may have additional requirements and are beyond the scope of this document.

## Installing MicroK8s

For each node that will be in the cluster run the following commands to install MicroK8s along with its dependencies. These steps must be performed on each node individually. Please review the contents of [microk8s/install.sh](microk8s/install.sh) and [microk8s/install_addons.sh](./microk8s/install_addons.sh) as these scripts will install additional components on your system as well as make changes to your groups and environment variables.

### Step 1: Install MicroK8s Base

#### Command
```bash
cd ./samples/kubernetes
sudo -E ./microk8s/install.sh
```

#### Expected Output
```text
<snip>
Assigning <user name> to microk8s group
```

> NOTE: If you are running behind a proxy please ensure that your `NO_PROXY` and `no_proxy` environment variables are set correctly to allow cluster nodes to communicate directly. You can run these commands to set this up automatically:
> ```bash
> UPDATE_NO_PROXY=true sudo -E ./microk8s/install.sh
> su - $USER
> ```

### Step 2: Activate Group Membership

Your user is now a member of a newly added 'microk8s' group. However, the current terminal session will not be aware of this until you issue this command:

#### Command

```bash
newgrp microk8s
groups | grep microk8s
```

#### Expected Output
```text
<snip> microk8s <snip>
```

### Step 3: Install MicroK8s Add-Ons

Next we need to install add-on components into the cluster. These enable Docker Registry and DNS.

#### Command

```bash
./microk8s/install_addons.sh
```

Note that this script may take **several minutes** to complete.

#### Expected Output

```text
Started.
Metrics-Server is enabled
DNS is enabled
Ingress is enabled
Metrics-Server is enabled
DNS is enabled
The registry is enabled
```

The `install_addons.sh` script automatically monitors for the Kubernetes system pods to reach the `Running` state. This may take a few minutes. During this phase it reports:
```text
One or more dependent services are in non-Running state...
One or more dependent services are in non-Running state...
<snip>
Confirming nodes are ready...
Dependent services are now ready..
```

### Step 4: Wait for Kubernetes System Pods to Reach Running State

At this point we need to wait for the Kubernetes system pods to reach the running state. This may take a few minutes.

Check that the installation was successful by confirming `STATUS` is `Running` for all pods. Pods will cycle through `ContainerCreating`, `Pending`, and `Waiting` states but all should eventually reach the `Running` state. After a few minutes if all pods do not reach the `Running` state refer to [application cluster troubleshooting tips](https://kubernetes.io/docs/tasks/debug-application-cluster/debug-pod-replication-controller/) for more help.

> Troubleshooting Tip: If you see `Pending` or `ContainerCreating` after waiting more than a few minutes, you may need to modify your environment variables with respect to proxy settings and restart MicroK8s. Do this by running `microk8s stop`, modifying the environment variables in your shell, and then running `microk8s start`. Then check the status of pods by running this command again.

#### Command

```bash
microk8s kubectl get pods --all-namespaces
```

#### Expected Output

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

### Step 5: Setup Proxy Server DNS
> Note: This step is required if you are running behind proxy, skip otherwise.

Use the following steps to set up the MicroK8s DNS service correctly.

#### 1. Identify host network’s configured DNS servers

##### Command

```bash
systemd-resolve --status | grep "Current DNS" --after-context=3
```

##### Expected Output

```text
Current DNS Server: 10.22.1.1
       DNS Servers: <ip1>
                    <ip2>
                    <ip3>
```

#### 2. Disable MicroK8s DNS

##### Command

```bash
microk8s disable dns
```

##### Expected Output

```text
Disabling DNS
Reconfiguring kubelet
Removing DNS manifest
serviceaccount "coredns" deleted
configmap "coredns" deleted
deployment.apps "coredns" deleted
service "kube-dns" deleted
clusterrole.rbac.authorization.k8s.io "coredns" deleted
clusterrolebinding.rbac.authorization.k8s.io "coredns" deleted
DNS is disabled
```

#### 3. Enable DNS with Host DNS Server

##### Command

```bash
microk8s enable dns:<ip1>,<ip2>,<ip3>
```

##### Expected Output

```text
Enabling DNS
Applying manifest
serviceaccount/coredns created
configmap/coredns created
deployment.apps/coredns created
service/kube-dns created
clusterrole.rbac.authorization.k8s.io/coredns created
clusterrolebinding.rbac.authorization.k8s.io/coredns created
Restarting kubelet
DNS is enabled
```

#### 4. Confirm Update

##### Command

```bash
sh -c "until microk8s.kubectl rollout status deployments/coredns -n kube-system -w; do sleep 5; done"
```

##### Expected Output

```text
deployment "coredns" successfully rolled out
```

## Adding Node to the Cluster

> Note: This step is only required if you have 2 or more nodes, skip otherwise.

### Step 1: Select Leader and Add Node

Choose one of your nodes as the `leader` node.

For each additional node that will be in the cluster, issue the following command on the `leader` node. You will need to do this once for each node you want to add.

#### Command

```bash
microk8s add-node
```

#### Expected Output

You should see output as follows, including the IP address of the primary/controller host and unique token for the node you are adding to use during connection to the cluster.

```bash
From the node you wish to join to this cluster, run the following:
microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889

If the node you are adding is not reachable through the default interface you can use one of the following:
 microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
 microk8s join 172.17.0.1:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
```

### Step 2: Join Node to Cluster

Run  `join` command shown in the above response on each `worker node` to be added.

#### Command

```bash
microk8s join <leader-ip>:25000/02c66e66e811fe2c697b1cd5d31bfba2/023e49528889
```

#### Expected Output

```text
Contacting cluster at <leader-ip>
Waiting for this node to finish joining the cluster. ..
```

If you encounter an error `Connection failed. Invalid token (500)` your token may have expired or you already used it for another node. To resolve, run the `add-node` command on the leader node to get a new token.

### Step 3: Confirm Cluster Nodes

To confirm what nodes are running in your cluster, run:

#### Command

```bash
microk8s kubectl get no
```

#### Expected Output

```text
NAME         STATUS   ROLES    AGE   VERSION
vcplab003    Ready    <none>   3d    v1.21.5-3+83e2bb7ee39726
vcplab002    Ready    <none>   84s   v1.21.5-3+83e2bb7ee39726
```

## Removing Node from Cluster

### Confirm Running Nodes

To confirm what nodes are running in your cluster, run:

#### Command

```bash
microk8s kubectl get no
```

#### Expected Output

```text
NAME           STATUS     ROLES    AGE   VERSION
<node-name>    Ready      <none>   96d   v1.21.9-3+5bfa682137fad9
```

### Drain Node

Drain the node, run below command in worker node you want to remove

#### Command

```bash
microk8s kubectl drain <node-name> --ignore-daemonsets
```

#### Expected Output

```text
<snip>
node/<node-name> drained
```

### Leave Cluster

Run below command in worker node you want to remove to leave the cluster

```bash
microk8s leave
```

### Remove Node

Run below command on **leader node**

```bash
microk8s remove-node <node-name/ip>
```

## Uninstalling Microk8s

### Step 1: Undeploy Pipeline Server, HAProxy and MQTT services

Follow steps to [Undeploy Services](../README.md#undeploy-services)

### Step 2: Remove Node

Follow steps to [Removing nodes from cluster](#removing-node-from-cluster)

### Step 3: Uninstall MicroK8s

#### Command

```bash
./microk8s/uninstall.sh
```

#### Expected Output

```text
==========================
Remove/Purge microk8s
==========================
microk8s removed
```
