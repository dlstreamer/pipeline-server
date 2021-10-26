#!/bin/bash
IMAGE=dlstreamer-edge-ai-extension
docker logs -f $IMAGE | python3 samples/ava_ai_extension/stream_density/stream_density.py
