#!/bin/bash

# Purpose:
#   sudo ./install_addons.sh is responsible for post-install configuration of microk8s.
# Outcome:
#   Upon successful completion, microk8s and sub-services are running and this host is
#   prepared for deploying as a node to process our scaled workloads.

WORK_DIR=$(dirname $(readlink -f "$0"))
SCRIPT_NAME=$(basename -- "$0")
SKIP_CHECKS=${SKIP_CHECKS:-false}

function launch { $@
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "ERROR: error with $1" >&2
        echo "Recommend you re-run ./install.sh to ensure dependencies are in place."
        exit $exit_code
    fi
    return $exit_code
}

# Sanity check
groups | grep microk8s
if [ ${PIPESTATUS[1]} != 0 ]; then
  echo "NOT A MEMBER OF microk8s GROUP! You may need to run ./install.sh, newgrp microk8s, logout/relaunch your terminal, reboot ( or start a new session using  su - \$USER )"
  exit
fi
if [[ ! -z "$HTTP_PROXY" ]] || [[ ! -z "$HTTPS_PROXY" ]] || [[ ! -z "$http_proxy" ]] || [[ ! -z "$https_proxy" ]]; then
  echo "Proxy server configuration was detected."
  echo $no_proxy | grep "10.1.0.0"
  if [ ${PIPESTATUS[1]} != 0 ]; then
    echo "Assignments for network environment are missing! Check if these are being overridden by ~/.bashrc, /etc/bash.bashrc or equivalents. Re-run install.sh, logout/relaunch your terminal, reboot ( or start a new session using  su - \$USER )"
    exit
  fi
else
  echo "No proxy server configuration was detected."
fi

# ===============================
# Install Add-ons
# ===============================

launch microk8s start
sleep 5
launch microk8s enable dashboard dns ingress metrics-server storage registry

if [ "$SKIP_CHECKS" == "false" ]; then
  echo "Confirming dependent services are running..."
  sleep 3
  # Sanity check to confirm all dependent services are running.
  for (( i=0; i<20; ++i)); do
    non_running_status=$(microk8s kubectl get pods --all-namespaces | awk '{ print $4 }' | grep -vE 'Running|STATUS')
    if [ -z "$non_running_status" ]; then
      echo "All Services are in Running state."
      break
    else
      echo "One or more dependent services are in non-Running state..."
      sleep 10
    fi
  done

  echo "Confirming nodes are ready..."
  sleep 3
  # Wait for configured nodes to be in ready state
  for (( i=0; i<20; ++i)); do
    non_running_status=$(microk8s kubectl wait -n registry --for=condition=ready pod --all 2>&1)
    if [[ "$non_running_status" == *"try microk8s start"* ]]; then
      echo "You appear to have forgotten to run ./install_addons.sh or microk8s start"
      exit
    fi
    if [ $? -ne 0 ]; then
      echo "Dependent services are not yet ready.."
      echo $non_running_status
      sleep 10
    else
      non_running_status=$(microk8s kubectl wait --for=condition=ready pod --all 2>&1)
      echo "Dependent services are now ready.."
      break
    fi
  done
else
  echo "DANGER: You have skipped checks and microk8s system may not be ready!"
fi
