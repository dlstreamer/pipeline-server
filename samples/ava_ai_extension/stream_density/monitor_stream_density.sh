#!/bin/bash
IMAGE=dlstreamer-edge-ai-extension
docker logs -f $IMAGE | python3 samples/ava_ai_extension/ignite_demo/stream_density.py
