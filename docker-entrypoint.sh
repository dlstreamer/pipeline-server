#!/bin/bash -e
cd app/server
python3 -m openapi_server $@
