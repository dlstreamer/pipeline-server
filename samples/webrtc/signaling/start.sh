#!/bin/bash
#
# Copyright (C) 2022 Intel Corporation.
#
# SPDX-License-Identifier: BSD-3-Clause
#
echo "Running Signaling Server entrypoint start.sh"

# Launch signaling server
python -u ./simple_server.py --disable-ssl