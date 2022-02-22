#!/bin/bash

echo "=========================="
echo "Reset microk8s, it may take more time"
echo "=========================="
microk8s reset

echo "=========================="
echo "Remove/Purge microk8s"
echo "=========================="
sudo snap remove --purge microk8s