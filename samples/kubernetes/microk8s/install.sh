#!/bin/bash

# Purpose:
#   sudo ./install.sh is responsible for installation of microk8s and related
#   dependencies used to prepare the k8s cluster.
# Outcome:
#   Upon successful completion, microk8s is installed and this host is prepared for deploying
#   as a node to process our scaled workloads.


WORK_DIR=$(dirname $(readlink -f "$0"))
SCRIPT_NAME=$(basename -- "$0")

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root/sudo"
  echo "sudo -E ./$SCRIPT_NAME"
  exit
fi

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        echo "Recommend you re-run ./install.sh to ensure dependencies are in place."
        exit $exit_code
    fi
    return $exit_code
}

# ===============================
# Prepare Network Environment
# ===============================
#
# If you encounter issues, refer to https://microk8s.io/docs/install-proxy
#
# CAUTION: Unreliable to parse IP address or make assumptions.
#          Order is not guaranteed and multi-NIC systems.
ADD_HOSTNAME=$HOSTNAME
ADD_IP_ADDR=$(hostname -I | cut -d' ' -f1)
echo "Is your host IP address $ADD_IP_ADDR? If not you must modify the install.sh script to add the correct value."
read -n 1 -s -r -p "Press any key to continue"
echo "."

# Local host loopbacks defined in /etc/hosts
ADD_LOOPBACKS=localhost,127.0.1.1,127.0.0.1
# Docker k8s network nodes
ADD_CLUSTER_NODES=10.1.0.0/16,10.152.183.0/24

# Assign Hostname once
if [[ "$no_proxy" != *"$ADD_HOSTNAME"* ]]; then
  echo "Adding HostName [$ADD_HOSTNAME] to no_proxy."
  no_proxy=$no_proxy,$ADD_HOSTNAME
fi
if [[ "$NO_PROXY" != *"$ADD_HOSTNAME"* ]]; then
  echo "Adding HostName [$ADD_HOSTNAME] to NO_PROXY."
  NO_PROXY=$NO_PROXY,$ADD_HOSTNAME
fi

# Assign IP Address once
if [[ "$no_proxy" != *"$ADD_IP_ADDR"* ]]; then
  echo "Adding IP Address [$ADD_IP_ADDR] to no_proxy."
  no_proxy=$no_proxy,$ADD_IP_ADDR
fi
if [[ "$NO_PROXY" != *"$ADD_IP_ADDR"* ]]; then
  echo "Adding IP Address [$ADD_IP_ADDR] to NO_PROXY."
  NO_PROXY=$NO_PROXY,$ADD_IP_ADDR
fi

# Assign Loopbacks once
if [[ "$no_proxy" != *"$ADD_LOOPBACKS"* ]]; then
  echo "Adding Loopbacks [$ADD_LOOPBACKS] to no_proxy."
  no_proxy=$no_proxy,$ADD_LOOPBACKS
fi
if [[ "$NO_PROXY" != *"$ADD_LOOPBACKS"* ]]; then
  echo "Adding Loopbacks [$ADD_LOOPBACKS] to NO_PROXY."
  NO_PROXY=$NO_PROXY,$ADD_LOOPBACKS
fi

# Assign ClusterNodes once
if [[ "$no_proxy" != *"$ADD_CLUSTER_NODES"* ]]; then
  echo "Adding ClusterNodes [$ADD_CLUSTER_NODES] to no_proxy."
  no_proxy=$no_proxy,${ADD_CLUSTER_NODES}
fi
if [[ "$NO_PROXY" != *"$ADD_CLUSTER_NODES"* ]]; then
  echo "Adding ClusterNodes [$ADD_CLUSTER_NODES] to NO_PROXY."
  NO_PROXY=$NO_PROXY,${ADD_CLUSTER_NODES}
fi

# Add to /etc/environment so vars are picked up immediately
# and persists across reboots. Takes affect for all users on this host.
echo "no_proxy=$(echo $no_proxy)" >> /etc/environment
echo "NO_PROXY=$(echo $NO_PROXY)" >> /etc/environment
echo "no_proxy=$(echo $no_proxy)" >> /etc/bash.bashrc
echo "NO_PROXY=$(echo $NO_PROXY)" >> /etc/bash.bashrc

# Enable traffic forwarding
launch iptables -P FORWARD ACCEPT

# ===============================
# Installation
# ===============================
launch snap install microk8s --classic --channel=1.21/stable
echo "Assigning $SUDO_USER to microk8s group"
launch usermod -a -G microk8s $SUDO_USER
# Create and assign current user as owner for cache
mkdir -p ~/.kube
launch chown -f -R $SUDO_USER ~/.kube
