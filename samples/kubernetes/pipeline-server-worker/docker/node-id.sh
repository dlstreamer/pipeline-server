#!/bin/bash
ID=$(cat /sys/class/net/eth0/address | sed 's/://g' | tr -d '\n')
echo "$ID"