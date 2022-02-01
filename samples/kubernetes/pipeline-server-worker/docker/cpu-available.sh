#!/bin/bash
# This outputs a 1 second average CPU idle
LOAD=$(/usr/bin/vmstat 1 2 | /usr/bin/tail -1 | /usr/bin/awk '{ print $15 }' | /usr/bin/tee)

# Considering 96% of CPU utilization is considered as 100%
if [ $LOAD -lt 5 ]; then
    LOAD=0
fi
echo "$LOAD%"