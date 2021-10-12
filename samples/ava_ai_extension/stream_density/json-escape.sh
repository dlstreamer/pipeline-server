#!/bin/bash
cat "$1" | jq -c | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' | sed -e 's/\\n//'
